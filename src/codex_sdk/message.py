"""Message class for handling Codex responses with streaming and final retrieval."""

import asyncio
from typing import Optional, AsyncIterator, Any

from .exceptions import MessageError


class Message:
    """
    Represents a message response from Codex with support for streaming and final retrieval.

    Usage:
        # Streaming approach
        for part in message:
            print(part)  # Handle delta events
        final = await message.get()  # Get complete message

        # Direct approach (ignore streaming)
        final = await message.get()
    """

    def __init__(self, result_or_task: Any, event_stream: Optional[AsyncIterator] = None, session=None):
        """Initialize with the MCP tool call result/task and optional event stream."""
        self._result_or_task = result_or_task
        self._event_stream = event_stream
        self._session = session
        self._final_text: Optional[str] = None
        self._extracted = False
        self._streamed_text = ""
        self._result_cache: Optional[Any] = None
        self._task_completed = False

    async def __aiter__(self) -> AsyncIterator[str]:
        """
        Async iterator for streaming delta events.

        Yields incremental text chunks as they arrive from Codex streaming events.
        """
        if self._event_stream:
            # Stream from real events
            async for event in self._event_stream:
                # Only yield agent_message_delta events (actual response text)
                if event.get('type') == 'agent_message_delta':
                    delta = event.get('delta', '')
                    if delta:
                        self._streamed_text += delta
                        yield delta
        else:
            # Fallback: if no event stream, yield the complete response
            if not self._extracted:
                await self._extract_text()
            if self._final_text:
                yield self._final_text

    async def get(self) -> str:
        """
        Get the complete final message text.

        This method works both after streaming and without streaming.

        Returns:
            The complete message text from Codex.

        Raises:
            MessageError: If the message text cannot be extracted.
        """
        # Always ensure the task completes to avoid TaskGroup errors
        await self._get_result()

        # If we have streamed text, return it
        if self._streamed_text:
            return self._streamed_text

        # Extract from final result
        if not self._extracted:
            await self._extract_text()

        if self._final_text is None:
            raise MessageError("Failed to extract message text from response")

        return self._final_text

    async def _get_result(self) -> Any:
        """Get the result, waiting for task completion if needed."""
        if self._result_cache is not None:
            return self._result_cache

        # Check if this is a task or a direct result
        if hasattr(self._result_or_task, 'done') and callable(self._result_or_task.done):
            # It's an asyncio Task
            try:
                result = await self._result_or_task
                self._result_cache = result
                self._task_completed = True

                # Update conversation ID in session if needed
                if self._session and not self._session._conversation_id:
                    self._session._conversation_id = self._session._extract_conversation_id(result)

                return result
            except Exception as e:
                self._task_completed = True
                raise
        else:
            # It's a direct result
            self._result_cache = self._result_or_task
            return self._result_or_task

    def __del__(self):
        """Cleanup when message is destroyed."""
        # Cancel the task if it's still running to prevent TaskGroup errors
        if (hasattr(self._result_or_task, 'done') and
            callable(self._result_or_task.done) and
            not self._task_completed and
            not self._result_or_task.done()):
            self._result_or_task.cancel()

    async def _extract_text(self) -> None:
        """Extract the text content from the MCP result."""
        if self._extracted:
            return

        result = await self._get_result()

        try:
            if hasattr(result, 'content') and result.content:
                text_parts = []
                for item in result.content:
                    if hasattr(item, 'text'):
                        text_parts.append(item.text)

                if text_parts:
                    self._final_text = '\n'.join(text_parts)
                else:
                    self._final_text = ""
            else:
                self._final_text = ""

        except Exception as e:
            raise MessageError(f"Failed to extract text from response: {e}")

        finally:
            self._extracted = True