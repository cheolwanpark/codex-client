"""Client class for managing Codex MCP connections and conversations."""

import asyncio
from contextlib import AsyncExitStack
from typing import Any, AsyncIterator, Dict, Optional, Tuple

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from .chat import Chat
from .config import CodexChatConfig
from .event import AllEvents
from .exceptions import ConnectionError, ToolError
from .middleware import setup_mcp_middleware


# Set up MCP middleware for streaming and warning suppression
_middleware = setup_mcp_middleware()


class Client:
    """Manages the MCP connection and spawns chats for Codex conversations."""

    def __init__(
        self,
        command: str = "codex",
        args: Optional[list[str]] = None,
        env: Optional[Dict[str, str]] = None,
        **_: Any,
    ) -> None:
        if args is None:
            args = ["mcp", "serve"]

        self._server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env,
        )
        self._session: Optional[ClientSession] = None
        self._exit_stack: Optional[AsyncExitStack] = None

    async def __aenter__(self) -> "Client":
        try:
            self._exit_stack = AsyncExitStack()

            read_stream, write_stream = await self._exit_stack.enter_async_context(
                stdio_client(self._server_params)
            )

            self._session = await self._exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )

            await self._session.initialize()

            return self

        except Exception as exc:
            if self._exit_stack:
                await self._exit_stack.aclose()
            raise ConnectionError(f"Failed to connect to Codex MCP server: {exc}")

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._exit_stack:
            await self._exit_stack.aclose()

        if _middleware:
            _middleware.clear_events()

        self._session = None

    async def create_chat(
        self,
        prompt: str,
        config: Optional[CodexChatConfig] = None,
    ) -> Chat:
        """Spawn a new chat by sending the initial prompt to Codex."""

        chat = Chat(self)
        config = config or CodexChatConfig()

        try:
            await chat._start(
                prompt=prompt,
                config=config,
            )
        except Exception as exc:
            raise ToolError(f"Failed to start chat: {exc}") from exc

        return chat

    def _ensure_session(self) -> ClientSession:
        if not self._session:
            raise ConnectionError("Not connected to Codex server. Use 'async with Client()' syntax.")
        return self._session

    def _build_initial_tool_args(
        self,
        *,
        prompt: str,
        config: CodexChatConfig,
    ) -> Tuple[str, Dict[str, Any]]:
        tool_args: Dict[str, Any] = {"prompt": prompt}

        tool_args.update(config.model_dump(exclude_none=True))

        return "codex", tool_args

    def _build_resume_tool_args(
        self,
        *,
        conversation_id: str,
        prompt: str,
    ) -> Tuple[str, Dict[str, Any]]:
        tool_args: Dict[str, Any] = {
            "conversationId": conversation_id,
            "prompt": prompt,
        }

        return "codex-reply", tool_args

    def _call_tool(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
    ) -> Tuple[asyncio.Task, Optional[AsyncIterator[AllEvents]]]:
        session = self._ensure_session()

        import json
        print(json.dumps(tool_args, indent=2))

        if _middleware:
            _middleware.clear_events()

        task = asyncio.create_task(session.call_tool(tool_name, tool_args))

        event_stream: Optional[AsyncIterator[AllEvents]] = None
        if _middleware:
            event_stream = _middleware.get_event_stream()

        return task, event_stream

    @property
    def is_connected(self) -> bool:
        return self._session is not None
