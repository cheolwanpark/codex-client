"""Optional aggregated chat stream helpers built on top of raw Codex events."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import contextlib
from typing import AsyncIterator, Dict, Generic, List, Optional, TypeVar, Union

from .event import (
    AgentMessageDeltaEvent,
    AgentMessageEvent,
    AgentReasoningDeltaEvent,
    AgentReasoningEvent,
    Duration,
    EventMsg,
    ExecCommandBeginEvent,
    ExecCommandEndEvent,
    ExecCommandOutputDeltaEvent,
    ExecOutputStream,
)

T = TypeVar("T")


class _AsyncStreamBuffer(Generic[T]):
    """Utility to buffer items while allowing streaming consumption."""

    def __init__(self) -> None:
        self._items: List[T] = []
        self._data_ready = asyncio.Event()
        self._completed = asyncio.Event()
        self._stream_started = False

    @property
    def items(self) -> List[T]:
        return self._items

    def append(self, item: T) -> None:
        self._items.append(item)
        self._data_ready.set()

    def finish(self) -> None:
        self._completed.set()
        self._data_ready.set()

    def has_items(self) -> bool:
        return bool(self._items)

    def is_complete(self) -> bool:
        return self._completed.is_set()

    async def iter(self) -> AsyncIterator[T]:
        if self._stream_started:
            raise RuntimeError("stream() already consumed")
        self._stream_started = True
        index = 0
        while True:
            while index < len(self._items):
                yield self._items[index]
                index += 1
            if self._completed.is_set():
                break
            self._data_ready.clear()
            await self._data_ready.wait()

    async def wait_complete(self) -> None:
        await self._completed.wait()


@dataclass
class CommandOutputChunk:
    """Command output chunk with stream metadata."""

    stream: ExecOutputStream
    data: bytes
    text: Optional[str]


class AssistantMessageStream:
    """Aggregated assistant message with streaming access to deltas."""

    def __init__(self, sequence: int, conversation_id: Optional[str]) -> None:
        self.sequence = sequence
        self.conversation_id = conversation_id
        self._buffer: _AsyncStreamBuffer[str] = _AsyncStreamBuffer()
        self._final_event: Optional[AgentMessageEvent] = None

    def add_delta(self, delta: str) -> None:
        self._buffer.append(delta)

    def complete(self, event: AgentMessageEvent) -> None:
        self._final_event = event
        if not self._buffer.has_items() and event.message:
            self._buffer.append(event.message)
        self._buffer.finish()

    async def stream(self) -> AsyncIterator[str]:
        async for chunk in self._buffer.iter():
            yield chunk

    async def wait_complete(self) -> None:
        await self._buffer.wait_complete()

    @property
    def message(self) -> Optional[str]:
        if self._final_event:
            return self._final_event.message
        if self._buffer.has_items():
            return "".join(self._buffer.items)
        return None

    @property
    def is_complete(self) -> bool:
        return self._buffer.is_complete()


class ReasoningStream:
    """Aggregated reasoning stream similar to assistant message handling."""

    def __init__(self, sequence: int, conversation_id: Optional[str]) -> None:
        self.sequence = sequence
        self.conversation_id = conversation_id
        self._buffer: _AsyncStreamBuffer[str] = _AsyncStreamBuffer()
        self._final_event: Optional[AgentReasoningEvent] = None

    def add_delta(self, delta: str) -> None:
        self._buffer.append(delta)

    def complete(self, event: AgentReasoningEvent) -> None:
        self._final_event = event
        if not self._buffer.has_items() and event.text:
            self._buffer.append(event.text)
        self._buffer.finish()

    async def stream(self) -> AsyncIterator[str]:
        async for chunk in self._buffer.iter():
            yield chunk

    async def wait_complete(self) -> None:
        await self._buffer.wait_complete()

    @property
    def text(self) -> Optional[str]:
        if self._final_event:
            return self._final_event.text
        if self._buffer.has_items():
            return "".join(self._buffer.items)
        return None

    @property
    def is_complete(self) -> bool:
        return self._buffer.is_complete()


class CommandStream:
    """Aggregated command execution stream."""

    def __init__(self, begin: ExecCommandBeginEvent, sequence: int) -> None:
        self.sequence = sequence
        self.call_id = begin.call_id
        self.command = begin.command
        self.cwd = begin.cwd
        self.parsed_cmd = begin.parsed_cmd
        self.begin_event = begin
        self._buffer: _AsyncStreamBuffer[CommandOutputChunk] = _AsyncStreamBuffer()
        self.exit_code: Optional[int] = None
        self.duration: Optional[Duration] = None
        self.stdout: Optional[str] = None
        self.stderr: Optional[str] = None
        self.aggregated_output: Optional[str] = None
        self.formatted_output: Optional[str] = None
        self.end_event: Optional[ExecCommandEndEvent] = None

    def add_output(self, event: ExecCommandOutputDeltaEvent) -> None:
        data = event.decoded_chunk
        try:
            text = event.decoded_text
        except UnicodeDecodeError:
            text = None
        self._buffer.append(CommandOutputChunk(stream=event.stream, data=data, text=text))

    def complete(self, event: ExecCommandEndEvent) -> None:
        self.end_event = event
        self.exit_code = event.exit_code
        self.duration = event.duration
        self.stdout = event.stdout
        self.stderr = event.stderr
        self.aggregated_output = event.aggregated_output
        self.formatted_output = event.formatted_output
        if event.aggregated_output and not self._buffer.has_items():
            # Provide something for consumers even if no deltas streamed.
            self._buffer.append(
                CommandOutputChunk(stream=ExecOutputStream.STDOUT, data=event.aggregated_output.encode(), text=event.aggregated_output)
            )
        self._buffer.finish()

    async def stream(self) -> AsyncIterator[CommandOutputChunk]:
        async for chunk in self._buffer.iter():
            yield chunk

    async def wait_complete(self) -> None:
        await self._buffer.wait_complete()

    @property
    def is_complete(self) -> bool:
        return self._buffer.is_complete()


AggregatedChatEvent = Union[
    AssistantMessageStream,
    ReasoningStream,
    CommandStream,
    EventMsg,
]


async def structured(chat: AsyncIterator[EventMsg]) -> AsyncIterator[AggregatedChatEvent]:
    """Yield aggregated wrappers while preserving access to raw events."""

    stop_token = object()
    queue: "asyncio.Queue[AggregatedChatEvent | object]" = asyncio.Queue()

    async def pump() -> None:
        assistant_stream: Optional[AssistantMessageStream] = None
        reasoning_stream: Optional[ReasoningStream] = None
        command_streams: Dict[str, CommandStream] = {}

        assistant_seq = 0
        reasoning_seq = 0
        command_seq = 0

        try:
            async for event in chat:
                if isinstance(event, AgentMessageDeltaEvent):
                    if assistant_stream is None:
                        assistant_seq += 1
                        assistant_stream = AssistantMessageStream(assistant_seq, event.conversation_id)
                        assistant_stream.add_delta(event.delta)
                        await queue.put(assistant_stream)
                    else:
                        assistant_stream.add_delta(event.delta)
                    continue

                if isinstance(event, AgentMessageEvent):
                    if assistant_stream is None:
                        assistant_seq += 1
                        assistant_stream = AssistantMessageStream(assistant_seq, event.conversation_id)
                        assistant_stream.complete(event)
                        await queue.put(assistant_stream)
                        assistant_stream = None
                    else:
                        assistant_stream.complete(event)
                        assistant_stream = None
                    continue

                if isinstance(event, AgentReasoningDeltaEvent):
                    if reasoning_stream is None:
                        reasoning_seq += 1
                        reasoning_stream = ReasoningStream(reasoning_seq, event.conversation_id)
                        reasoning_stream.add_delta(event.delta)
                        await queue.put(reasoning_stream)
                    else:
                        reasoning_stream.add_delta(event.delta)
                    continue

                if isinstance(event, AgentReasoningEvent):
                    if reasoning_stream is None:
                        reasoning_seq += 1
                        reasoning_stream = ReasoningStream(reasoning_seq, event.conversation_id)
                        reasoning_stream.complete(event)
                        await queue.put(reasoning_stream)
                        reasoning_stream = None
                    else:
                        reasoning_stream.complete(event)
                        reasoning_stream = None
                    continue

                if isinstance(event, ExecCommandBeginEvent):
                    command_seq += 1
                    stream = CommandStream(event, command_seq)
                    command_streams[event.call_id] = stream
                    await queue.put(stream)
                    continue

                if isinstance(event, ExecCommandOutputDeltaEvent):
                    stream = command_streams.get(event.call_id)
                    if stream is None:
                        await queue.put(event)
                        continue
                    stream.add_output(event)
                    continue

                if isinstance(event, ExecCommandEndEvent):
                    stream = command_streams.pop(event.call_id, None)
                    if stream is None:
                        await queue.put(event)
                        continue
                    stream.complete(event)
                    continue

                await queue.put(event)
        finally:
            if assistant_stream and not assistant_stream.is_complete:
                assistant_stream._buffer.finish()  # best effort flush
            if reasoning_stream and not reasoning_stream.is_complete:
                reasoning_stream._buffer.finish()
            for stream in command_streams.values():
                if not stream.is_complete:
                    stream._buffer.finish()
            await queue.put(stop_token)

    pump_task = asyncio.create_task(pump())

    try:
        while True:
            item = await queue.get()
            if item is stop_token:
                break
            yield item  # type: ignore[misc]
        await pump_task
    finally:
        if not pump_task.done():
            pump_task.cancel()
            with contextlib.suppress(Exception):
                await pump_task


__all__ = [
    "AggregatedChatEvent",
    "AssistantMessageStream",
    "CommandOutputChunk",
    "CommandStream",
    "ReasoningStream",
    "structured",
]
