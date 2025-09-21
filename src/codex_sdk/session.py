"""Session class for managing Codex MCP connections and interactions."""

import asyncio
from typing import Optional, Dict, Any, Union, AsyncIterator
from contextlib import AsyncExitStack

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from .message import Message
from .exceptions import ConnectionError, ToolError
from .middleware import setup_mcp_middleware
from .event import CodexEventMsg


# Set up MCP middleware for streaming and warning suppression
_middleware = setup_mcp_middleware()


class Session:
    """
    Manages connection to Codex MCP server and provides chat interface.

    Usage:
        async with Session() as session:
            message = await session.chat("Hello!")
            response = await message.get()
    """

    def __init__(
        self,
        command: str = "codex",
        args: Optional[list[str]] = None,
        env: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize a new Codex session.

        Args:
            command: Command to start the MCP server (default: "codex")
            args: Arguments for the command (default: ["mcp", "serve"])
            env: Environment variables for the subprocess
            **kwargs: Additional arguments (for future extensibility)
        """
        if args is None:
            args = ["mcp", "serve"]

        self._server_params: StdioServerParameters = StdioServerParameters(
            command=command,
            args=args,
            env=env,
        )
        self._session: Optional[ClientSession] = None
        self._exit_stack: Optional[AsyncExitStack] = None
        self._conversation_id: Optional[str] = None

    async def __aenter__(self) -> "Session":
        """Enter the async context manager and establish connection."""
        try:
            self._exit_stack = AsyncExitStack()

            # Connect to the MCP server
            read_stream, write_stream = await self._exit_stack.enter_async_context(
                stdio_client(self._server_params)
            )

            # Create and initialize the session
            self._session = await self._exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )

            await self._session.initialize()

            return self

        except Exception as e:
            if self._exit_stack:
                await self._exit_stack.aclose()
            raise ConnectionError(f"Failed to connect to Codex MCP server: {e}")

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the async context manager and clean up resources."""
        if self._exit_stack:
            await self._exit_stack.aclose()

        # Clean up middleware resources
        if _middleware:
            _middleware.clear_events()

        self._session = None
        self._conversation_id = None

    async def chat(
        self,
        prompt: str,
        sandbox: Union[str, bool] = "read-only",
        approval_policy: str = "never",
        **kwargs: Any
    ) -> AsyncIterator[Message]:
        """
        Send a chat message to Codex and return an async iterator of Message objects.

        Args:
            prompt: The message to send to Codex
            sandbox: Sandbox mode ("read-only", True, False, etc.)
            approval_policy: Approval policy ("never", "always", etc.)
            **kwargs: Additional tool parameters

        Yields:
            Message objects that support streaming and final retrieval

        Raises:
            ConnectionError: If not connected to the server
            ToolError: If the tool call fails
        """
        if not self._session:
            raise ConnectionError("Not connected to Codex server. Use 'async with Session()' syntax.")

        try:
            # Prepare tool arguments
            tool_args: Dict[str, Any] = {
                "prompt": prompt,
                **kwargs
            }

            # Add sandbox parameter if provided
            if sandbox is not None:
                if isinstance(sandbox, bool):
                    tool_args["sandbox"] = "read-only" if sandbox else None
                else:
                    tool_args["sandbox"] = sandbox

            # Add approval policy
            tool_args["approval-policy"] = approval_policy

            # Determine which tool to use
            tool_name = "codex-reply" if self._conversation_id else "codex"

            # Add conversation ID for continuation
            if self._conversation_id:
                tool_args["conversationId"] = self._conversation_id

            # Clear any previous events before making the tool call
            if _middleware:
                _middleware.clear_events()

            # Start the tool call as a background task
            tool_task = asyncio.create_task(
                self._session.call_tool(tool_name, tool_args)
            )

            # Create event stream that will capture events during the tool call
            event_stream: Optional[AsyncIterator[CodexEventMsg]] = None
            if _middleware:
                event_stream = _middleware.get_event_stream()

            # Yield message immediately so streaming can start in parallel
            yield Message(tool_task, event_stream, self)

        except Exception as e:
            raise ToolError(f"Tool call failed: {e}")

    def _extract_conversation_id(self, result: Any) -> Optional[str]:
        """
        Try to extract conversation ID from the response.

        Note: Based on the demo code, conversation ID extraction is not reliable
        from the response text. This is a best-effort implementation.
        """
        import re

        if not (hasattr(result, 'content') and result.content):
            return None

        for content_item in result.content:
            if hasattr(content_item, 'text'):
                text = content_item.text

                # Look for UUID patterns that might be conversation IDs
                uuid_pattern = r'\\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\\b'
                matches = re.findall(uuid_pattern, text, re.IGNORECASE)
                if matches:
                    return matches[0]

        return None

    @property
    def is_connected(self) -> bool:
        """Check if the session is connected."""
        return self._session is not None

    @property
    def conversation_id(self) -> Optional[str]:
        """Get the current conversation ID, if available."""
        return self._conversation_id
