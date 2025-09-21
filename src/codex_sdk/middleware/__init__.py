"""Integrated Codex MCP middleware that emits typed events."""

from __future__ import annotations

import asyncio
import logging
from typing import AsyncIterator, Optional

from ..event import CodexEventMsg, AllEvents
from .filter import CodexEventFilter


class CodexMiddleware:
    """Capture Codex MCP events and expose them as an async stream."""

    def __init__(self) -> None:
        self._event_queue: "asyncio.Queue[AllEvents]" = asyncio.Queue()
        self._filter = CodexEventFilter(self._event_queue)

    def install(self) -> None:
        """Attach the filter to the root logger and silence MCP warnings."""

        root_logger = logging.getLogger()
        root_logger.addFilter(self._filter)
        logging.getLogger("mcp").setLevel(logging.ERROR)

    async def get_event_stream(self) -> AsyncIterator[AllEvents]:
        """Yield typed events as they are captured from Codex."""

        consecutive_timeouts = 0
        max_consecutive_timeouts = 300

        while True:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                consecutive_timeouts = 0
                yield event

                if getattr(event, "type", None) == "task_complete":
                    break
            except asyncio.TimeoutError:
                consecutive_timeouts += 1
                if consecutive_timeouts >= max_consecutive_timeouts:
                    break

    def clear_events(self) -> None:
        """Remove any queued events."""

        while not self._event_queue.empty():
            try:
                self._event_queue.get_nowait()
            except asyncio.QueueEmpty:
                break


_middleware_instance: Optional[CodexMiddleware] = None


def setup_mcp_middleware() -> CodexMiddleware:
    """Create (or return) the global Codex middleware instance."""

    global _middleware_instance

    if _middleware_instance is None:
        _middleware_instance = CodexMiddleware()
        _middleware_instance.install()

    return _middleware_instance


def get_middleware() -> Optional[CodexMiddleware]:
    """Return the global middleware instance if one has been created."""

    return _middleware_instance


__all__ = [
    "CodexMiddleware",
    "get_middleware",
    "setup_mcp_middleware",
]
