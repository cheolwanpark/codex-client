"""Codex SDK - A minimal library for programmatic control of Codex.

Example:
    from codex_sdk import Client

    async with Client() as client:
        chat = await client.create_chat("Hello, Codex!")

        async for event in chat:
            print(event)

        await chat.resume("Can you elaborate?")
"""

from .client import Client
from .chat import Chat
from .config import (
    CodexChatConfig,
    CodexMcpServer,
    CodexProfile,
    ApprovalPolicy,
    SandboxMode,
    ReasoningEffort,
    Verbosity,
)
from .exceptions import CodexError, ConnectionError, ChatError, ToolError
from .event import (
    AgentMessageDeltaEvent,
    AgentMessageEvent,
    AgentReasoningDeltaEvent,
    AgentReasoningEvent,
    AgentReasoningSectionBreakEvent,
    CodexEventMsg,
    Duration,
    EventMetadata,
    ExecCommandBeginEvent,
    ExecCommandEndEvent,
    ExecCommandOutputDeltaEvent,
    ExecOutputStream,
    McpToolCallBeginEvent,
    McpToolCallEndEvent,
    SessionConfiguredEvent,
    TaskCompleteEvent,
    TaskStartedEvent,
    TokenCountEvent,
    parse_event,
)
from .structured import (
    AssistantMessageStream,
    CommandStream,
    ReasoningStream,
    structured,
)
from .middleware import setup_mcp_middleware, get_middleware

__version__ = "0.1.0"

__all__ = [
    # Core SDK
    "Client",
    "Chat",
    "CodexError",
    "ConnectionError",
    "ChatError",
    "ToolError",

    # Config
    "CodexChatConfig",
    "CodexProfile",
    "CodexMcpServer",
    "ApprovalPolicy",
    "SandboxMode",
    "ReasoningEffort",
    "Verbosity",

    # Events
    "AgentMessageDeltaEvent",
    "AgentMessageEvent",
    "AgentReasoningDeltaEvent",
    "AgentReasoningEvent",
    "AgentReasoningSectionBreakEvent",
    "CodexEventMsg",
    "Duration",
    "EventMetadata",
    "ExecCommandBeginEvent",
    "ExecCommandEndEvent",
    "ExecCommandOutputDeltaEvent",
    "ExecOutputStream",
    "McpToolCallBeginEvent",
    "McpToolCallEndEvent",
    "SessionConfiguredEvent",
    "TaskCompleteEvent",
    "TaskStartedEvent",
    "TokenCountEvent",
    "parse_event",

    # Structured stream helpers
    "structured",
    "AssistantMessageStream",
    "ReasoningStream",
    "CommandStream",

    # Middleware
    "setup_mcp_middleware",
    "get_middleware",
]
