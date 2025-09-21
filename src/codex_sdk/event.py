"""Typed Codex MCP event models and parsing utilities."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Type, Union

from pydantic import BaseModel, ConfigDict, Field


class EventMetadata(BaseModel):
    """Metadata emitted alongside each Codex MCP event."""

    request_id: int = Field(..., alias="requestId")

    model_config = ConfigDict(populate_by_name=True)


class Duration(BaseModel):
    """Duration information reported by the Codex server."""

    secs: int
    nanos: int

    def total_seconds(self) -> float:
        """Return the duration expressed as seconds."""

        return self.secs + self.nanos / 1_000_000_000


class CodexEvent(BaseModel):
    """Base class for all Codex MCP events."""

    type: str
    meta: EventMetadata = Field(..., alias="_meta")

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class AgentMessageEvent(CodexEvent):
    type: Literal["agent_message"] = "agent_message"
    message: str


class AgentMessageDeltaEvent(CodexEvent):
    type: Literal["agent_message_delta"] = "agent_message_delta"
    delta: str


class AgentReasoningEvent(CodexEvent):
    type: Literal["agent_reasoning"] = "agent_reasoning"
    text: str


class AgentReasoningDeltaEvent(CodexEvent):
    type: Literal["agent_reasoning_delta"] = "agent_reasoning_delta"
    delta: str


class AgentReasoningSectionBreakEvent(CodexEvent):
    type: Literal["agent_reasoning_section_break"] = "agent_reasoning_section_break"


class ExecCommandBeginEvent(CodexEvent):
    type: Literal["exec_command_begin"] = "exec_command_begin"
    call_id: str
    command: List[Any]
    cwd: str
    parsed_cmd: List[Any]


class ExecCommandEndEvent(CodexEvent):
    type: Literal["exec_command_end"] = "exec_command_end"
    aggregated_output: str
    call_id: str
    duration: Duration
    exit_code: int
    formatted_output: str
    stderr: str
    stdout: str


ExecOutputStream = Literal["stdout", "stderr"]


class ExecCommandOutputDeltaEvent(CodexEvent):
    type: Literal["exec_command_output_delta"] = "exec_command_output_delta"
    call_id: str
    chunk: str
    stream: ExecOutputStream


class McpToolInvocation(BaseModel):
    server: str
    tool: str
    arguments: Dict[str, Any]

class McpToolCallBeginEvent(CodexEvent):
    type: Literal["mcp_tool_call_begin"] = "mcp_tool_call_begin"
    call_id: str
    invocation: McpToolInvocation

class McpToolOkResult(BaseModel):
    Ok: Dict[str, Any]

class McpToolCallEndEvent(CodexEvent):
    type: Literal["mcp_tool_call_end"] = "mcp_tool_call_end"
    call_id: str
    duration: Duration
    invocation: McpToolInvocation
    result: McpToolOkResult


class SessionConfiguredEvent(CodexEvent):
    type: Literal["session_configured"] = "session_configured"
    history_entry_count: int
    history_log_id: int
    model: str
    rollout_path: str
    session_id: str


class TaskCompleteEvent(CodexEvent):
    type: Literal["task_complete"] = "task_complete"
    last_agent_message: str


class TaskStartedEvent(CodexEvent):
    type: Literal["task_started"] = "task_started"
    model_context_window: int


class TokenCountEvent(CodexEvent):
    type: Literal["token_count"] = "token_count"
    info: Dict[str, Any]


CodexEventMsg = Union[
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
]


_EVENT_CLASS_MAP: Dict[str, Type[CodexEvent]] = {
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


__all__ = [
    "AgentMessageDeltaEvent",
    "AgentMessageEvent",
    "AgentReasoningDeltaEvent",
    "AgentReasoningEvent",
    "AgentReasoningSectionBreakEvent",
    "CodexEvent",
    "CodexEventMsg",
    "Duration",
    "EventMetadata",
    "ExecOutputStream",
    "ExecCommandBeginEvent",
    "ExecCommandEndEvent",
    "ExecCommandOutputDeltaEvent",
    "McpToolCallBeginEvent",
    "McpToolCallEndEvent",
    "SessionConfiguredEvent",
    "TaskCompleteEvent",
    "TaskStartedEvent",
    "TokenCountEvent",
    "parse_event",
]
