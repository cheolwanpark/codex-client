"""Chat wrapper that manages Codex conversations and event streaming."""

from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator, Dict, List, Optional, TYPE_CHECKING, Union

from .event import CodexEventMsg, TaskCompleteEvent, SessionConfiguredEvent, AllEvents
from .exceptions import ChatError

if TYPE_CHECKING:
    from .client import Client


class Chat:
    """Represents a Codex conversation with streaming events and resume support."""

    def __init__(self, client: "Client") -> None:
        self._client = client
        self._conversation_id: Optional[str] = None

        self._result_or_task: Optional[Any] = None
        self._result_cache: Optional[Any] = None
        self._task_completed = False

        self._events: List[CodexEventMsg] = []
        self._iter_index = 0
        self._events_complete = True
        self._event_available: asyncio.Event = asyncio.Event()
        self._event_available.set()
        self._stream_task: Optional[asyncio.Task[None]] = None
        self._stream_error: Optional[BaseException] = None
        self._last_agent_message: Optional[str] = None

    def __aiter__(self) -> "Chat":
        return self

    async def __anext__(self) -> CodexEventMsg:
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
        await self._get_result()
        await self._ensure_events_collected()

        if self._last_agent_message is not None:
            return self._last_agent_message

        raise ChatError("Task completion event not received or missing last_agent_message")

    async def resume(self, prompt: str) -> None:
        if not self._conversation_id:
            await self._get_result()
            await self._ensure_events_collected()

        if not self._conversation_id:
            raise ChatError("Cannot resume before the initial turn completes")

        tool_name, tool_args = self._client._build_resume_tool_args(
            conversation_id=self._conversation_id,
            prompt=prompt,
        )
        await self._launch_tool(tool_name, tool_args)

    @property
    def conversation_id(self) -> Optional[str]:
        return self._conversation_id

    async def _start(
        self,
        *,
        prompt: str,
        sandbox: Union[str, bool, None],
        approval_policy: str,
        extra_tool_args: Dict[str, Any],
    ) -> None:
        tool_name, tool_args = self._client._build_initial_tool_args(
            prompt=prompt,
            sandbox=sandbox,
            approval_policy=approval_policy,
            extra_tool_args=extra_tool_args,
        )

        await self._launch_tool(tool_name, tool_args)

    async def _launch_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> None:
        self._cancel_pending_tasks()

        task, event_stream = self._client._call_tool(tool_name, tool_args)

        self._result_or_task = task
        self._result_cache = None
        self._task_completed = False

        self._events = []
        self._iter_index = 0
        self._events_complete = event_stream is None
        self._event_available = asyncio.Event()
        self._stream_task = None
        self._stream_error = None
        self._last_agent_message = None

        if event_stream is not None:
            self._stream_task = asyncio.create_task(self._consume_events(event_stream))
        else:
            self._event_available.set()

    async def _consume_events(self, event_stream: AsyncIterator[AllEvents]) -> None:
        try:
            async for event in event_stream:
                self._events.append(event)

                conversation_id = getattr(event, "conversation_id", None)
                if not conversation_id and isinstance(event, SessionConfiguredEvent):
                    conversation_id = event.session_id
                if conversation_id:
                    self._conversation_id = conversation_id
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
            raise ChatError("Failed to stream Codex events") from self._stream_error

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

        result_or_task = self._result_or_task
        if result_or_task and hasattr(result_or_task, "done") and callable(result_or_task.done):
            try:
                result = await result_or_task
                self._result_cache = result
                self._task_completed = True

                conversation_id = self._extract_conversation_id(result)
                if conversation_id:
                    self._conversation_id = conversation_id

                return result
            except Exception:
                self._task_completed = True
                raise

        self._result_cache = result_or_task
        return result_or_task

    def _cancel_pending_tasks(self) -> None:
        if self._stream_task and not self._stream_task.done():
            self._stream_task.cancel()

        if (
            self._result_or_task
            and hasattr(self._result_or_task, "done")
            and callable(self._result_or_task.done)
            and not self._result_or_task.done()
        ):
            self._result_or_task.cancel()

        self._result_or_task = None

    @staticmethod
    def _extract_conversation_id(result: Any) -> Optional[str]:
        import re

        if not (hasattr(result, "content") and result.content):
            return None

        for content_item in result.content:
            if hasattr(content_item, "text"):
                text = content_item.text

                uuid_pattern = r"\\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\\b"
                matches = re.findall(uuid_pattern, text, re.IGNORECASE)
                if matches:
                    return matches[0]

        return None

    def __del__(self) -> None:
        self._cancel_pending_tasks()
