"""Message wrapper that streams Codex MCP events and exposes final output."""

from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator, List, Optional, TYPE_CHECKING

from .event import CodexEventMsg, TaskCompleteEvent
from .exceptions import MessageError

if TYPE_CHECKING:
    from .session import Session


class Message:
    """Represents a Codex response with streaming Codex events and final text access."""

    def __init__(
        self,
        result_or_task: Any,
        event_stream: Optional[AsyncIterator[CodexEventMsg]] = None,
        session: Optional["Session"] = None,
    ) -> None:
        self._result_or_task = result_or_task
        self._session = session

        self._result_cache: Optional[Any] = None
        self._task_completed = False

        self._events: List[CodexEventMsg] = []
        self._iter_index = 0
        self._events_complete = event_stream is None
        self._event_available: asyncio.Event = asyncio.Event()
        self._stream_task: Optional[asyncio.Task[None]] = None
        self._stream_error: Optional[BaseException] = None
        self._last_agent_message: Optional[str] = None

        if event_stream is not None:
            self._stream_task = asyncio.create_task(self._consume_events(event_stream))
        else:
            self._event_available.set()

    def __aiter__(self) -> "Message":
        """Return self so the message can be iterated for streaming events."""

        return self

    async def __anext__(self) -> CodexEventMsg:
        """Return the next Codex event from the stream."""

        while True:
            if self._iter_index < len(self._events):
                event = self._events[self._iter_index]
                self._iter_index += 1
                return event

            if self._events_complete:
                self._check_stream_error()
                raise StopAsyncIteration

            await self._wait_for_next_event()
            self._check_stream_error()

    async def get(self) -> str:
        """Return the final message taken from the TaskComplete event."""

        await self._get_result()
        await self._ensure_events_collected()

        if self._last_agent_message is not None:
            return self._last_agent_message

        raise MessageError("Task completion event not received or missing last_agent_message")

    async def _consume_events(self, event_stream: AsyncIterator[CodexEventMsg]) -> None:
        try:
            async for event in event_stream:
                self._events.append(event)
                if isinstance(event, TaskCompleteEvent):
                    self._last_agent_message = event.last_agent_message
                self._event_available.set()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self._stream_error = exc
            self._event_available.set()
            raise
        finally:
            self._events_complete = True
            self._event_available.set()

    async def _wait_for_next_event(self) -> None:
        await self._event_available.wait()
        self._event_available.clear()

    def _check_stream_error(self) -> None:
        if self._stream_error:
            raise MessageError("Failed to stream Codex events") from self._stream_error

    async def _ensure_events_collected(self) -> None:
        if self._stream_task:
            try:
                await self._stream_task
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                if self._stream_error is None:
                    self._stream_error = exc
        self._check_stream_error()

    async def _get_result(self) -> Any:
        if self._result_cache is not None:
            return self._result_cache

        if hasattr(self._result_or_task, "done") and callable(self._result_or_task.done):
            try:
                result = await self._result_or_task
                self._result_cache = result
                self._task_completed = True

                if self._session and not self._session._conversation_id:
                    self._session._conversation_id = self._session._extract_conversation_id(result)

                return result
            except Exception:
                self._task_completed = True
                raise

        self._result_cache = self._result_or_task
        return self._result_or_task

    def __del__(self) -> None:
        if (
            hasattr(self._result_or_task, "done")
            and callable(self._result_or_task.done)
            and not self._task_completed
            and not self._result_or_task.done()
        ):
            self._result_or_task.cancel()

        if self._stream_task and not self._stream_task.done():
            self._stream_task.cancel()
