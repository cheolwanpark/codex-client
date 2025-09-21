# Codex Event Response Schema (MCP Mode)

This document provides comprehensive documentation of the Codex MCP event system, including all event types, their JSON schemas, and corresponding Python BaseModel implementations based on the authoritative Rust source code.

## Overview

The Codex SDK uses a streaming event-based protocol to communicate real-time updates during task execution in MCP (Model Context Protocol) mode. Events are emitted by the Codex server as JSON-RPC notifications.

### Complete JSON-RPC Notification Structure

All Codex events are sent as JSON-RPC notifications with this exact structure:

```json
{
  "jsonrpc": "2.0",
  "method": "codex/event",
  "params": {
    "_meta": {
      "requestId": 123
    },
    "id": "submission_id",
    "msg": {
      "type": "event_type",
      ...event_specific_fields
    }
  }
}
```

### Supporting Types

#### Duration
```python
class Duration(BaseModel):
    secs: int
    nanos: int

    def total_seconds(self) -> float:
        return self.secs + self.nanos / 1_000_000_000
```

#### Token Usage Types
```python
class TokenUsage(BaseModel):
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    reasoning_output_tokens: int
    total_tokens: int

class TokenUsageInfo(BaseModel):
    total_token_usage: TokenUsage
    last_token_usage: TokenUsage
    model_context_window: Optional[int]
```

#### MCP Content Types
```python
class TextContent(BaseModel):
    type: Literal["text"] = "text"
    text: str
    annotations: Optional[Dict[str, Any]] = None

class ImageContent(BaseModel):
    type: Literal["image"] = "image"
    data: str  # base64 encoded
    mime_type: str = Field(..., alias="mimeType")
    annotations: Optional[Dict[str, Any]] = None

class AudioContent(BaseModel):
    type: Literal["audio"] = "audio"
    data: str  # base64 encoded
    mime_type: str = Field(..., alias="mimeType")
    annotations: Optional[Dict[str, Any]] = None

class ResourceLink(BaseModel):
    type: Literal["resource"] = "resource"
    resource: Dict[str, Any]

class EmbeddedResource(BaseModel):
    type: Literal["resource"] = "resource"
    resource: Dict[str, Any]

ContentBlock = Union[TextContent, ImageContent, AudioContent, ResourceLink, EmbeddedResource]
```

#### MCP Tool Result Types (with Rust Result wrapper)
```python
class CallToolResult(BaseModel):
    content: List[ContentBlock]
    is_error: Optional[bool] = Field(None, alias="isError")
    structured_content: Optional[Dict[str, Any]] = Field(None, alias="structuredContent")

# Rust Result<CallToolResult, String> serialization
class OkResult(BaseModel):
    Ok: CallToolResult

class ErrResult(BaseModel):
    Err: str

ResultType = Union[OkResult, ErrResult]
```

#### MCP Tool Invocation
```python
class McpInvocation(BaseModel):
    server: str
    tool: str
    arguments: Optional[Dict[str, Any]]
```

#### Parsed Command Types (Tagged Enum with Discriminator)
```python
from typing import Annotated

class ReadCommand(BaseModel):
    type: Literal["read"] = "read"
    cmd: str
    name: str

class ListFilesCommand(BaseModel):
    type: Literal["list_files"] = "list_files"
    cmd: str
    path: Optional[str]

class SearchCommand(BaseModel):
    type: Literal["search"] = "search"
    cmd: str
    query: Optional[str]
    path: Optional[str]

class UnknownCommand(BaseModel):
    type: Literal["unknown"] = "unknown"
    cmd: str

# Optimized discriminated union for faster parsing
ParsedCommand = Annotated[
    Union[ReadCommand, ListFilesCommand, SearchCommand, UnknownCommand],
    Field(discriminator="type")
]
```

#### Reasoning Effort (Lowercase)
```python
class ReasoningEffort(str, Enum):
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
```

#### Stream Types
```python
class ExecOutputStream(str, Enum):
    STDOUT = "stdout"
    STDERR = "stderr"
```

#### Base JSON-RPC and Event Types
```python
class OutgoingNotificationMeta(BaseModel):
    request_id: Optional[Union[str, int]] = Field(None, alias="requestId")

class EventMsg(BaseModel):
    type: str

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
    meta: Optional[OutgoingNotificationMeta] = Field(None, alias="_meta")
    id: str
    msg: AllEvents  # Use discriminated union instead of generic EventMsg

class JsonRpcNotification(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["codex/event"] = "codex/event"
    params: McpEventParams
```

---

## Event Type Definitions

### 1. agent_message

Complete text message from the agent.

**JSON Schema:**
```json
{
  "type": "object",
  "properties": {
    "jsonrpc": {"const": "2.0"},
    "method": {"const": "codex/event"},
    "params": {
      "type": "object",
      "properties": {
        "_meta": {"$ref": "#/definitions/OutgoingNotificationMeta"},
        "id": {"type": "string"},
        "msg": {
          "type": "object",
          "properties": {
            "type": {"const": "agent_message"},
            "message": {"type": "string"}
          },
          "required": ["type", "message"]
        }
      },
      "required": ["id", "msg"]
    }
  },
  "required": ["jsonrpc", "method", "params"]
}
```

**BaseModel:**
```python
class AgentMessageEvent(EventMsg):
    type: Literal["agent_message"] = "agent_message"
    message: str
```

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "codex/event",
  "params": {
    "_meta": {"requestId": 123},
    "id": "submission_001",
    "msg": {
      "type": "agent_message",
      "message": "I'll help you implement the feature you requested."
    }
  }
}
```

---

### 2. agent_message_delta

Incremental text chunks from agent for streaming display.

**BaseModel:**
```python
class AgentMessageDeltaEvent(EventMsg):
    type: Literal["agent_message_delta"] = "agent_message_delta"
    delta: str
```

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "codex/event",
  "params": {
    "_meta": {"requestId": 123},
    "id": "submission_001",
    "msg": {
      "type": "agent_message_delta",
      "delta": "I'll help you"
    }
  }
}
```

---

### 3. agent_reasoning

Agent's reasoning text for transparent decision-making.

**BaseModel:**
```python
class AgentReasoningEvent(EventMsg):
    type: Literal["agent_reasoning"] = "agent_reasoning"
    text: str
```

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "codex/event",
  "params": {
    "_meta": {"requestId": 123},
    "id": "submission_001",
    "msg": {
      "type": "agent_reasoning",
      "text": "First, I need to understand the existing code structure..."
    }
  }
}
```

---

### 4. agent_reasoning_delta

Incremental reasoning text chunks for streaming.

**BaseModel:**
```python
class AgentReasoningDeltaEvent(EventMsg):
    type: Literal["agent_reasoning_delta"] = "agent_reasoning_delta"
    delta: str
```

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "codex/event",
  "params": {
    "_meta": {"requestId": 123},
    "id": "submission_001",
    "msg": {
      "type": "agent_reasoning_delta",
      "delta": "First, I need to"
    }
  }
}
```

---

### 5. agent_reasoning_section_break

Section separator in agent reasoning output.

**BaseModel:**
```python
class AgentReasoningSectionBreakEvent(EventMsg):
    type: Literal["agent_reasoning_section_break"] = "agent_reasoning_section_break"
```

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "codex/event",
  "params": {
    "_meta": {"requestId": 123},
    "id": "submission_001",
    "msg": {
      "type": "agent_reasoning_section_break"
    }
  }
}
```

---

### 6. exec_command_begin

Notification that command execution is starting.

**BaseModel:**
```python
class ExecCommandBeginEvent(EventMsg):
    type: Literal["exec_command_begin"] = "exec_command_begin"
    call_id: str
    command: List[str]
    cwd: str
    parsed_cmd: List[ParsedCommand]  # Tagged enum, not simple {name, args}
```

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "codex/event",
  "params": {
    "_meta": {"requestId": 123},
    "id": "submission_001",
    "msg": {
      "type": "exec_command_begin",
      "call_id": "cmd_001",
      "command": ["rg", "FastMCP", "src/"],
      "cwd": "/workspace",
      "parsed_cmd": [
        {
          "type": "search",
          "cmd": "rg FastMCP src/",
          "query": "FastMCP",
          "path": "src/"
        }
      ]
    }
  }
}
```

---

### 7. exec_command_end

Command execution completion with results.

**BaseModel:**
```python
class ExecCommandEndEvent(EventMsg):
    type: Literal["exec_command_end"] = "exec_command_end"
    call_id: str
    stdout: str
    stderr: str
    aggregated_output: str
    exit_code: int
    duration: Duration
    formatted_output: str
```

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "codex/event",
  "params": {
    "_meta": {"requestId": 123},
    "id": "submission_001",
    "msg": {
      "type": "exec_command_end",
      "call_id": "cmd_001",
      "stdout": "src/main.py:1:import FastMCP",
      "stderr": "",
      "aggregated_output": "src/main.py:1:import FastMCP",
      "exit_code": 0,
      "duration": {"secs": 0, "nanos": 120000000},
      "formatted_output": "✓ Found 1 match"
    }
  }
}
```

---

### 8. exec_command_output_delta

Real-time output chunks from running commands (base64 encoded).

**BaseModel:**
```python
import base64

class ExecOutputStream(str, Enum):
    STDOUT = "stdout"
    STDERR = "stderr"

class ExecCommandOutputDeltaEvent(EventMsg):
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
```

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "codex/event",
  "params": {
    "_meta": {"requestId": 123},
    "id": "submission_001",
    "msg": {
      "type": "exec_command_output_delta",
      "call_id": "cmd_001",
      "stream": "stdout",
      "chunk": "c3JjL21haW4ucHk6MTppbXBvcnQgRmFzdE1DUA=="
    }
  }
}
```

---

### 9. mcp_tool_call_begin

MCP tool invocation start notification.

**BaseModel:**
```python
class McpToolCallBeginEvent(EventMsg):
    type: Literal["mcp_tool_call_begin"] = "mcp_tool_call_begin"
    call_id: str
    invocation: McpInvocation
```

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "codex/event",
  "params": {
    "_meta": {"requestId": 123},
    "id": "submission_001",
    "msg": {
      "type": "mcp_tool_call_begin",
      "call_id": "call_v43ebeLbBFsCYfKAsaV2kUUv",
      "invocation": {
        "server": "context7",
        "tool": "resolve-library-id",
        "arguments": {
          "libraryName": "FastMCP"
        }
      }
    }
  }
}
```

---

### 10. mcp_tool_call_end

MCP tool invocation completion with Rust Result wrapper.

**BaseModel:**
```python
class McpToolCallEndEvent(EventMsg):
    type: Literal["mcp_tool_call_end"] = "mcp_tool_call_end"
    call_id: str
    invocation: McpInvocation
    duration: Duration
    result: ResultType  # Union[OkResult, ErrResult] - Rust Result wrapper
```

**Example (Success with Ok wrapper):**
```json
{
  "jsonrpc": "2.0",
  "method": "codex/event",
  "params": {
    "_meta": {"requestId": 2},
    "id": "2",
    "msg": {
      "type": "mcp_tool_call_end",
      "call_id": "call_v43ebeLbBFsCYfKAsaV2kUUv",
      "invocation": {
        "server": "context7",
        "tool": "resolve-library-id",
        "arguments": {
          "libraryName": "FastMCP"
        }
      },
      "duration": {
        "secs": 2,
        "nanos": 898869250
      },
      "result": {
        "Ok": {
          "content": [
            {
              "text": "Available Libraries (top matches):\n\n- Title: FastMCP\n- Context7-compatible library ID: /punkpeye/fastmcp\n- Description: FastMCP is a TypeScript framework...",
              "type": "text"
            }
          ]
        }
      }
    }
  }
}
```

**Example (Error with Err wrapper):**
```json
{
  "jsonrpc": "2.0",
  "method": "codex/event",
  "params": {
    "_meta": {"requestId": 124},
    "id": "submission_002",
    "msg": {
      "type": "mcp_tool_call_end",
      "call_id": "call_error_123",
      "invocation": {
        "server": "filesystem",
        "tool": "read_file",
        "arguments": {
          "path": "/nonexistent/file.txt"
        }
      },
      "duration": {
        "secs": 0,
        "nanos": 50000000
      },
      "result": {
        "Err": "File not found: /nonexistent/file.txt"
      }
    }
  }
}
```

---

### 11. session_configured

Session initialization acknowledgment with configuration details.

**BaseModel:**
```python
class SessionConfiguredEvent(EventMsg):
    type: Literal["session_configured"] = "session_configured"
    session_id: str
    model: str
    reasoning_effort: Optional[ReasoningEffort] = None  # lowercase values
    history_log_id: int
    history_entry_count: int
    initial_messages: Optional[List[EventMsg]] = None
    rollout_path: str
```

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "codex/event",
  "params": {
    "_meta": {"requestId": 123},
    "id": "submission_001",
    "msg": {
      "type": "session_configured",
      "session_id": "sess_12345",
      "model": "claude-3-5-sonnet",
      "reasoning_effort": "medium",
      "history_log_id": 67890,
      "history_entry_count": 0,
      "rollout_path": "/tmp/codex_session_12345"
    }
  }
}
```

---

### 12. task_complete

Task completion notification with final agent message.

**BaseModel:**
```python
class TaskCompleteEvent(EventMsg):
    type: Literal["task_complete"] = "task_complete"
    last_agent_message: Optional[str]
```

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "codex/event",
  "params": {
    "_meta": {"requestId": 123},
    "id": "submission_001",
    "msg": {
      "type": "task_complete",
      "last_agent_message": "Task completed successfully. All tests are passing."
    }
  }
}
```

---

### 13. task_started

Task execution start notification with model context information.

**BaseModel:**
```python
class TaskStartedEvent(EventMsg):
    type: Literal["task_started"] = "task_started"
    model_context_window: Optional[int]
```

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "codex/event",
  "params": {
    "_meta": {"requestId": 123},
    "id": "submission_001",
    "msg": {
      "type": "task_started",
      "model_context_window": 200000
    }
  }
}
```

---

### 14. token_count

Token usage statistics for the current session.

**BaseModel:**
```python
class TokenCountEvent(EventMsg):
    type: Literal["token_count"] = "token_count"
    info: Optional[TokenUsageInfo]
```

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "codex/event",
  "params": {
    "_meta": {"requestId": 123},
    "id": "submission_001",
    "msg": {
      "type": "token_count",
      "info": {
        "total_token_usage": {
          "input_tokens": 1500,
          "cached_input_tokens": 500,
          "output_tokens": 800,
          "reasoning_output_tokens": 200,
          "total_tokens": 2300
        },
        "last_token_usage": {
          "input_tokens": 100,
          "cached_input_tokens": 0,
          "output_tokens": 50,
          "reasoning_output_tokens": 10,
          "total_tokens": 150
        },
        "model_context_window": 200000
      }
    }
  }
}
```

---

## Union Type Definition

```python
EventMsgUnion = Union[
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
```

## Usage Examples

### Parsing JSON-RPC Notifications (Type-Safe with Discriminated Unions)

```python
import base64
from typing import Dict, Any, Annotated, Union
from pydantic import BaseModel, Field

def parse_codex_notification(raw_data: Dict[str, Any]) -> JsonRpcNotification:
    """Parse a JSON-RPC notification containing a Codex event.

    With discriminated unions, Pydantic automatically handles type detection
    and parsing based on the 'type' field.
    """

    # Validate JSON-RPC structure
    if raw_data.get("method") != "codex/event":
        raise ValueError("Not a codex/event notification")

    if raw_data.get("jsonrpc") != "2.0":
        raise ValueError("Invalid JSON-RPC version")

    # Pydantic automatically parses the correct event type using discriminator
    notification = JsonRpcNotification.model_validate(raw_data)

    return notification

# Example usage with type safety
notification_data = {
    "jsonrpc": "2.0",
    "method": "codex/event",
    "params": {
        "_meta": {"requestId": 123},
        "id": "submission_001",
        "msg": {
            "type": "agent_message",
            "message": "Hello, world!"
        }
    }
}

# Parse with automatic type detection
notification = parse_codex_notification(notification_data)

# Type-safe access to specific event fields
event_msg = notification.params.msg

# Python type checker and IDE know the specific type!
if event_msg.type == "agent_message":
    # event_msg is automatically typed as AgentMessageEvent
    print(f"Agent message: {event_msg.message}")
elif event_msg.type == "exec_command_output_delta":
    # event_msg is automatically typed as ExecCommandOutputDeltaEvent
    print(f"Command output: {event_msg.decoded_text}")  # Use helper property
elif event_msg.type == "mcp_tool_call_end":
    # event_msg is automatically typed as McpToolCallEndEvent
    if hasattr(event_msg.result, 'Ok'):
        print("Tool call succeeded")
        tool_result = event_msg.result.Ok  # Type-safe access
    elif hasattr(event_msg.result, 'Err'):
        print(f"Tool call failed: {event_msg.result.Err}")
```

### Handling Streaming Events (Type-Safe)

```python
import asyncio
import json
from typing import AsyncIterator

async def handle_codex_event_stream(event_stream: AsyncIterator[str]):
    """Handle streaming JSON-RPC notifications from Codex with type safety."""
    async for line in event_stream:
        try:
            raw_data = json.loads(line)
            notification = parse_codex_notification(raw_data)

            event_msg = notification.params.msg

            # Type-safe event handling with discriminated unions
            match event_msg.type:
                case "agent_message_delta":
                    print(event_msg.delta, end='', flush=True)

                case "exec_command_begin":
                    print(f"\n🔧 Running: {' '.join(event_msg.command)}")
                    # Show parsed command details with type safety
                    for cmd in event_msg.parsed_cmd:
                        match cmd.type:
                            case "search":
                                print(f"   Searching for: {cmd.query} in {cmd.path}")
                            case "read":
                                print(f"   Reading: {cmd.name}")
                            case "list_files":
                                path = cmd.path or "current directory"
                                print(f"   Listing files in: {path}")

                case "exec_command_output_delta":
                    # Use helper properties for clean decoding
                    try:
                        print(event_msg.decoded_text, end='')
                    except UnicodeDecodeError:
                        print(f"[binary: {len(event_msg.decoded_chunk)} bytes]")

                case "task_complete":
                    print(f"\n✅ Task completed: {event_msg.last_agent_message}")

                case "mcp_tool_call_end":
                    # Type-safe access to Result wrapper
                    if hasattr(event_msg.result, 'Ok'):
                        print(f"✅ Tool {event_msg.invocation.tool} succeeded")
                        # Access tool result content
                        for content in event_msg.result.Ok.content:
                            if content.type == "text":
                                print(f"   Result: {content.text[:100]}...")
                    elif hasattr(event_msg.result, 'Err'):
                        print(f"❌ Tool {event_msg.invocation.tool} failed: {event_msg.result.Err}")

                case "token_count":
                    if event_msg.info:
                        total = event_msg.info.total_token_usage.total_tokens
                        print(f"💰 Token usage: {total} total")

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Failed to parse notification: {e}")
```

### Working with ParsedCommand Enum (Type-Safe)

```python
def analyze_parsed_commands(parsed_cmds: List[ParsedCommand]):
    """Analyze the parsed command structure with full type safety."""
    for cmd in parsed_cmds:
        # Type-safe access with match statement
        match cmd.type:
            case "search":
                # cmd is automatically typed as SearchCommand
                query = cmd.query or "[no query]"
                path = cmd.path or "[no path]"
                print(f"Search command: query='{query}', path='{path}'")

            case "read":
                # cmd is automatically typed as ReadCommand
                print(f"Read command: name='{cmd.name}'")

            case "list_files":
                # cmd is automatically typed as ListFilesCommand
                path = cmd.path or "current directory"
                print(f"List files command: path='{path}'")

            case "unknown":
                # cmd is automatically typed as UnknownCommand
                print(f"Unknown command: '{cmd.cmd}'")

# Alternative approach using isinstance for older Python versions
def analyze_parsed_commands_legacy(parsed_cmds: List[ParsedCommand]):
    """Analyze commands using isinstance for Python < 3.10."""
    for cmd in parsed_cmds:
        if isinstance(cmd, SearchCommand):
            query = cmd.query or "[no query]"
            path = cmd.path or "[no path]"
            print(f"Search command: query='{query}', path='{path}'")
        elif isinstance(cmd, ReadCommand):
            print(f"Read command: name='{cmd.name}'")
        elif isinstance(cmd, ListFilesCommand):
            path = cmd.path or "current directory"
            print(f"List files command: path='{path}'")
        elif isinstance(cmd, UnknownCommand):
            print(f"Unknown command: '{cmd.cmd}'")
```

---

## References

- **Python SDK Event Names**: `src/codex_sdk/event.py`
- **Rust Protocol Definitions**: `codex/codex-rs/protocol/src/protocol.rs`
- **MCP Types**: `codex/codex-rs/mcp-types/src/lib.rs`
- **JSON-RPC Message Wrapping**: `codex/codex-rs/mcp-server/src/outgoing_message.rs`
- **ParsedCommand Definition**: `codex/codex-rs/protocol/src/parse_command.rs`
- **Config Types**: `codex/codex-rs/protocol/src/config_types.rs`