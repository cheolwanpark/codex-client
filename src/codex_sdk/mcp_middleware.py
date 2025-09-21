"""MCP middleware for streaming events and warning suppression."""

import asyncio
import json
import logging
import re
from typing import Dict, Optional, AsyncIterator, Any


class MCPStreamingMiddleware(logging.Filter):
    """Middleware that captures Codex streaming events and suppresses validation warnings."""

    def __init__(self):
        super().__init__()
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._active_sessions = set()

    def filter(self, record):
        """
        Filter out MCP validation warnings while capturing streaming events.

        Args:
            record: LogRecord to potentially filter

        Returns:
            False if the record should be filtered out, True otherwise
        """
        if hasattr(record, 'getMessage'):
            message = record.getMessage()

            # Check for codex/event validation warnings and extract streaming data
            if "Failed to validate notification" in message and "codex/event" in message:
                event_data = self._extract_codex_event(message)
                if event_data:
                    # Queue the event for streaming
                    self._queue_event(event_data)

                # Always suppress these validation warnings
                return False

            # Suppress other validation warnings too
            if "validation errors for ServerNotification" in message:
                return False

        return True

    def _extract_codex_event(self, warning_message: str) -> Optional[Dict[str, Any]]:
        """
        Extract codex/event data from MCP validation warning message.

        Parses messages like:
        "Message was: method='codex/event' params={'_meta': {...}, 'msg': {...}}"
        """
        try:
            # Look for the params JSON in the warning message
            # The pattern needs to capture nested braces properly
            match = re.search(r"params=(\{.*\}) jsonrpc=", warning_message, re.DOTALL)
            if not match:
                return None

            params_str = match.group(1)
            # Fix single quotes to double quotes for JSON parsing
            params_str = params_str.replace("'", '"')
            params = json.loads(params_str)

            # Extract relevant event data
            if 'msg' in params and '_meta' in params:
                event = params['msg']
                event['_meta'] = params['_meta']
                return event

        except (json.JSONDecodeError, AttributeError) as e:
            # If parsing fails, just ignore this event
            pass

        return None

    def _queue_event(self, event_data: Dict[str, Any]):
        """Queue an event."""
        try:
            # Queue the event (non-blocking)
            try:
                self._event_queue.put_nowait(event_data)
            except asyncio.QueueFull:
                # If queue is full, skip this event to prevent blocking
                pass

        except Exception:
            # If any error occurs in queuing, ignore silently to prevent breaking logging
            pass

    async def get_event_stream(self) -> AsyncIterator[Dict[str, Any]]:
        """
        Get streaming events.

        Yields:
            Event dictionaries containing streaming data
        """
        consecutive_timeouts = 0
        max_consecutive_timeouts = 50  # Allow up to 5 seconds of waiting (50 * 0.1s)

        while True:
            try:
                # Wait for an event with a short timeout
                event = await asyncio.wait_for(self._event_queue.get(), timeout=0.1)
                consecutive_timeouts = 0  # Reset timeout counter
                yield event

                # If this is a task_complete event, we're done
                if event.get('type') == 'task_complete':
                    break

            except asyncio.TimeoutError:
                consecutive_timeouts += 1
                if consecutive_timeouts >= max_consecutive_timeouts:
                    # Give up after too many consecutive timeouts
                    break
                # Continue waiting for more events

    def clear_events(self):
        """Clear all queued events."""
        while not self._event_queue.empty():
            try:
                self._event_queue.get_nowait()
            except asyncio.QueueEmpty:
                break


# Global middleware instance
_middleware_instance = None


def setup_mcp_middleware() -> MCPStreamingMiddleware:
    """
    Set up MCP middleware for streaming and warning suppression.

    Returns:
        The middleware instance for event access
    """
    global _middleware_instance

    if _middleware_instance is None:
        _middleware_instance = MCPStreamingMiddleware()

        # Apply middleware to root logger
        root_logger = logging.getLogger()
        root_logger.addFilter(_middleware_instance)

        # Also suppress MCP validation warnings at the logger level
        logging.getLogger("mcp").setLevel(logging.ERROR)

    return _middleware_instance


def get_middleware() -> Optional[MCPStreamingMiddleware]:
    """Get the current middleware instance if it exists."""
    return _middleware_instance