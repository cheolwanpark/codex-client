"""Typed Codex MCP event models and parsing utilities."""

from __future__ import annotations

import base64
from enum import Enum
from typing import Annotated, Any, Dict, List, Literal, Optional, Type, Union

from pydantic import BaseModel, ConfigDict, Field


# Supporting Types

class Duration(BaseModel):
    """Duration information reported by the Codex server."""

    secs: int
    nanos: int

    def total_seconds(self) -> float:
        """Return the duration expressed as seconds."""
        return self.secs + self.nanos / 1_000_000_000


class TokenUsage(BaseModel):
    """Token usage statistics."""

    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    reasoning_output_tokens: int
    total_tokens: int


class TokenUsageInfo(BaseModel):
    """Complete token usage information."""

    total_token_usage: TokenUsage
    last_token_usage: TokenUsage
    model_context_window: Optional[int] = None


# MCP Content Types

class TextContent(BaseModel):
    """Text content block."""

    type: Literal["text"] = "text"
    text: str
    annotations: Optional[Dict[str, Any]] = None


class ImageContent(BaseModel):
    """Image content block."""

    type: Literal["image"] = "image"
    data: str  # base64 encoded
    mime_type: str = Field(..., alias="mimeType")
    annotations: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(populate_by_name=True)


class AudioContent(BaseModel):
    """Audio content block."""

    type: Literal["audio"] = "audio"
    data: str  # base64 encoded
    mime_type: str = Field(..., alias="mimeType")
    annotations: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(populate_by_name=True)


class ResourceLink(BaseModel):
    """Resource link content block."""

    type: Literal["resource"] = "resource"
    resource: Dict[str, Any]


class EmbeddedResource(BaseModel):
    """Embedded resource content block."""

    type: Literal["resource"] = "resource"
    resource: Dict[str, Any]


ContentBlock = Union[TextContent, ImageContent, AudioContent, ResourceLink, EmbeddedResource]


# MCP Tool Result Types (with Rust Result wrapper)

class CallToolResult(BaseModel):
    """Result from MCP tool call."""

    content: List[ContentBlock]
    is_error: Optional[bool] = Field(None, alias="isError")
    structured_content: Optional[Dict[str, Any]] = Field(None, alias="structuredContent")

    model_config = ConfigDict(populate_by_name=True)


class OkResult(BaseModel):
    """Rust Result Ok wrapper."""

    Ok: CallToolResult


class ErrResult(BaseModel):
    """Rust Result Err wrapper."""

    Err: str


ResultType = Union[OkResult, ErrResult]


# MCP Tool Invocation

class McpInvocation(BaseModel):
    """MCP tool invocation details."""

    server: str
    tool: str
    arguments: Optional[Dict[str, Any]] = None


# Parsed Command Types (Tagged Enum with Discriminator)

class ReadCommand(BaseModel):
    """Read command representation."""

    type: Literal["read"] = "read"
    cmd: str
    name: str


class ListFilesCommand(BaseModel):
    """List files command representation."""

    type: Literal["list_files"] = "list_files"
    cmd: str
    path: Optional[str] = None


class SearchCommand(BaseModel):
    """Search command representation."""

    type: Literal["search"] = "search"
    cmd: str
    query: Optional[str] = None
    path: Optional[str] = None


class UnknownCommand(BaseModel):
    """Unknown command representation."""

    type: Literal["unknown"] = "unknown"
    cmd: str


# Optimized discriminated union for faster parsing
ParsedCommand = Annotated[
    Union[ReadCommand, ListFilesCommand, SearchCommand, UnknownCommand],
    Field(discriminator="type")
]


# Enums

class ReasoningEffort(str, Enum):
    """Reasoning effort levels (lowercase)."""

    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ExecOutputStream(str, Enum):
    """Execution output stream types."""

    STDOUT = "stdout"
    STDERR = "stderr"


# Base JSON-RPC and Event Types

class OutgoingNotificationMeta(BaseModel):
    """Metadata for outgoing notifications."""

    request_id: Optional[Union[str, int]] = Field(None, alias="requestId")

    model_config = ConfigDict(populate_by_name=True)


class EventMsg(BaseModel):
    """Base class for all event messages."""

    type: str


# Event Type Definitions

class AgentMessageEvent(EventMsg):
    """Complete text message from the agent."""

    type: Literal["agent_message"] = "agent_message"
    message: str


class AgentMessageDeltaEvent(EventMsg):
    """Incremental text chunks from agent for streaming display."""

    type: Literal["agent_message_delta"] = "agent_message_delta"
    delta: str


class AgentReasoningEvent(EventMsg):
    """Agent's reasoning text for transparent decision-making."""

    type: Literal["agent_reasoning"] = "agent_reasoning"
    text: str


class AgentReasoningDeltaEvent(EventMsg):
    """Incremental reasoning text chunks for streaming."""

    type: Literal["agent_reasoning_delta"] = "agent_reasoning_delta"
    delta: str


class AgentReasoningSectionBreakEvent(EventMsg):
    """Section separator in agent reasoning output."""

    type: Literal["agent_reasoning_section_break"] = "agent_reasoning_section_break"


class ExecCommandBeginEvent(EventMsg):
    """Notification that command execution is starting."""

    type: Literal["exec_command_begin"] = "exec_command_begin"
    call_id: str
    command: List[str]
    cwd: str
    parsed_cmd: List[ParsedCommand]


class ExecCommandEndEvent(EventMsg):
    """Command execution completion with results."""

    type: Literal["exec_command_end"] = "exec_command_end"
    call_id: str
    stdout: str
    stderr: str
    aggregated_output: str
    exit_code: int
    duration: Duration
    formatted_output: str


class ExecCommandOutputDeltaEvent(EventMsg):
    """Real-time output chunks from running commands (base64 encoded)."""

    type: Literal["exec_command_output_delta"] = "exec_command_output_delta"
    call_id: str
    stream: ExecOutputStream
    chunk: str  # Base64 encoded bytes from Rust Vec<u8>

    @property
    def decoded_chunk(self) -> bytes:
        """Decode the base64-encoded chunk to get the original bytes."""
        return base64.b64decode(self.chunk)

    @property
    def decoded_text(self) -> str:
        """Decode the chunk and convert to UTF-8 text. May raise UnicodeDecodeError."""
        return self.decoded_chunk.decode('utf-8')


class McpToolCallBeginEvent(EventMsg):
    """MCP tool invocation start notification."""

    type: Literal["mcp_tool_call_begin"] = "mcp_tool_call_begin"
    call_id: str
    invocation: McpInvocation


class McpToolCallEndEvent(EventMsg):
    """MCP tool invocation completion with Rust Result wrapper."""

    type: Literal["mcp_tool_call_end"] = "mcp_tool_call_end"
    call_id: str
    invocation: McpInvocation
    duration: Duration
    result: ResultType  # Union[OkResult, ErrResult] - Rust Result wrapper


class SessionConfiguredEvent(EventMsg):
    """Session initialization acknowledgment with configuration details."""

    type: Literal["session_configured"] = "session_configured"
    session_id: str
    model: str
    reasoning_effort: Optional[ReasoningEffort] = None  # lowercase values
    history_log_id: int
    history_entry_count: int
    initial_messages: Optional[List[EventMsg]] = None
    rollout_path: str


class TaskCompleteEvent(EventMsg):
    """Task completion notification with final agent message."""

    type: Literal["task_complete"] = "task_complete"
    last_agent_message: Optional[str] = None


class TaskStartedEvent(EventMsg):
    """Task execution start notification with model context information."""

    type: Literal["task_started"] = "task_started"
    model_context_window: Optional[int] = None


class TokenCountEvent(EventMsg):
    """Token usage statistics for the current session."""

    type: Literal["token_count"] = "token_count"
    info: Optional[TokenUsageInfo] = None


# Discriminated union of all possible event types for type-safe parsing
AllEvents = Annotated[
    Union[
        AgentMessageEvent,
        AgentMessageDeltaEvent,
        AgentReasoningEvent,
        AgentReasoningDeltaEvent,
        AgentReasoningSectionBreakEvent,
        ExecCommandBeginEvent,
        ExecCommandEndEvent,
        ExecCommandOutputDeltaEvent,
        McpToolCallBeginEvent,
        McpToolCallEndEvent,
        SessionConfiguredEvent,
        TaskCompleteEvent,
        TaskStartedEvent,
        TokenCountEvent,
    ],
    Field(discriminator="type")
]


class McpEventParams(BaseModel):
    """Parameters for MCP event notifications."""

    meta: Optional[OutgoingNotificationMeta] = Field(None, alias="_meta")
    id: str
    msg: AllEvents  # Use discriminated union instead of generic EventMsg

    model_config = ConfigDict(populate_by_name=True)


class JsonRpcNotification(BaseModel):
    """Complete JSON-RPC notification structure."""

    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["codex/event"] = "codex/event"
    params: McpEventParams


# Legacy compatibility types
CodexEventMsg = AllEvents
EventMetadata = OutgoingNotificationMeta


# Event class mapping for legacy parse_event function
_EVENT_CLASS_MAP: Dict[str, Type[EventMsg]] = {
    "agent_message": AgentMessageEvent,
    "agent_message_delta": AgentMessageDeltaEvent,
    "agent_reasoning": AgentReasoningEvent,
    "agent_reasoning_delta": AgentReasoningDeltaEvent,
    "agent_reasoning_section_break": AgentReasoningSectionBreakEvent,
    "exec_command_begin": ExecCommandBeginEvent,
    "exec_command_end": ExecCommandEndEvent,
    "exec_command_output_delta": ExecCommandOutputDeltaEvent,
    "mcp_tool_call_begin": McpToolCallBeginEvent,
    "mcp_tool_call_end": McpToolCallEndEvent,
    "session_configured": SessionConfiguredEvent,
    "task_complete": TaskCompleteEvent,
    "task_started": TaskStartedEvent,
    "token_count": TokenCountEvent,
}


def parse_event(event_data: Dict[str, Any]) -> CodexEventMsg:
    """Parse raw event payload into a typed Codex event."""
    event_type = event_data.get("type")

    if not isinstance(event_type, str):
        raise ValueError("Event payload is missing a 'type' field")

    event_class = _EVENT_CLASS_MAP.get(event_type)

    if not event_class:
        raise ValueError(f"Unsupported event type: {event_type}")

    return event_class.model_validate(event_data)


def parse_notification(notification_data: Dict[str, Any]) -> JsonRpcNotification:
    """Parse a complete JSON-RPC notification containing a Codex event."""
    if notification_data.get("method") != "codex/event":
        raise ValueError("Not a codex/event notification")

    if notification_data.get("jsonrpc") != "2.0":
        raise ValueError("Invalid JSON-RPC version")

    # Pydantic automatically parses the correct event type using discriminator
    return JsonRpcNotification.model_validate(notification_data)


__all__ = [
    # Event types
    "AgentMessageEvent",
    "AgentMessageDeltaEvent",
    "AgentReasoningEvent",
    "AgentReasoningDeltaEvent",
    "AgentReasoningSectionBreakEvent",
    "ExecCommandBeginEvent",
    "ExecCommandEndEvent",
    "ExecCommandOutputDeltaEvent",
    "McpToolCallBeginEvent",
    "McpToolCallEndEvent",
    "SessionConfiguredEvent",
    "TaskCompleteEvent",
    "TaskStartedEvent",
    "TokenCountEvent",

    # Supporting types
    "Duration",
    "TokenUsage",
    "TokenUsageInfo",
    "TextContent",
    "ImageContent",
    "AudioContent",
    "ResourceLink",
    "EmbeddedResource",
    "ContentBlock",
    "CallToolResult",
    "OkResult",
    "ErrResult",
    "ResultType",
    "McpInvocation",
    "ReadCommand",
    "ListFilesCommand",
    "SearchCommand",
    "UnknownCommand",
    "ParsedCommand",
    "ReasoningEffort",
    "ExecOutputStream",
    "OutgoingNotificationMeta",
    "EventMsg",
    "AllEvents",
    "McpEventParams",
    "JsonRpcNotification",

    # Legacy compatibility
    "CodexEventMsg",
    "EventMetadata",

    # Parsing functions
    "parse_event",
    "parse_notification",
]