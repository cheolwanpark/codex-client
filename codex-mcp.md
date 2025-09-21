# Codex MCP Server Documentation

## Description

The Codex MCP (Model Context Protocol) server provides programmatic access to Codex sessions through two primary tools. Codex is an AI-powered coding assistant that can execute complex, multi-step development tasks autonomously within various sandbox environments.

The server enables:
- **Autonomous Code Generation**: Execute complex coding tasks with minimal human intervention
- **Sandbox Execution**: Run code safely in controlled environments (read-only, workspace-write, or full access)
- **Session Management**: Start new sessions and continue existing conversations
- **Configurable Behavior**: Customize model selection, approval policies, and execution parameters

## Basic Instructions

### Getting Started

1. **Initialize a Codex Session**: Use `mcp__codex__codex` to start a new coding session with your requirements
2. **Continue Conversations**: Use `mcp__codex__codex-reply` to extend existing sessions with additional prompts
3. **Choose Appropriate Sandbox**: Select sandbox mode based on your security requirements
4. **Monitor Execution**: Review generated code and execution results

### Best Practices

- Start with `read-only` or `workspace-write` sandbox modes for safety
- Use specific, detailed prompts for better results
- Leverage conversation continuity for complex, multi-step projects
- Configure approval policies based on your trust level and security requirements

## Event Streaming System

The Codex MCP server provides a sophisticated **real-time event streaming system** that sends detailed notifications about session progress, command execution, and AI reasoning. Events are sent via MCP notifications using the method `"codex/event"`.

### Event Architecture

**Core Event Structure** (`codex/codex-rs/protocol/src/protocol.rs:419-451`):
```rust
pub struct Event {
    pub id: String,        // Submission ID for correlation
    pub msg: EventMsg,     // Event payload
}
```

### Event Categories

#### 1. Real-time Communication Events
- `AgentMessage` - Complete AI responses
- `AgentMessageDelta` - **Streaming text chunks as AI generates responses**
- `AgentReasoning` - High-level reasoning summaries
- `AgentReasoningDelta` - **Streaming reasoning updates in real-time**
- `AgentReasoningRawContent` - Detailed chain-of-thought content
- `AgentReasoningRawContentDelta` - **Streaming raw reasoning chunks**
- `AgentReasoningSectionBreak` - Reasoning section boundaries

#### 2. Command Execution Events
- `ExecCommandBegin` - Command execution starts
- `ExecCommandOutputDelta` - **Real-time stdout/stderr streaming**
- `ExecCommandEnd` - Command execution completes

**Command Output Delta Schema**:
```rust
pub struct ExecCommandOutputDeltaEvent {
    pub call_id: String,           // Links to ExecCommandBegin
    pub stream: ExecOutputStream,  // Stdout or Stderr
    pub chunk: Vec<u8>,           // Raw bytes (base64 encoded over wire)
}
```

#### 3. Tool & Action Events
- `McpToolCallBegin/End` - MCP tool invocations
- `WebSearchBegin/End` - Web search operations
- `PatchApplyBegin/End` - Code patch applications

#### 4. Approval & Interaction Events
- `ExecApprovalRequest` - Requests user permission for commands
- `ApplyPatchApprovalRequest` - Requests approval for code changes

#### 5. Session Management Events
- `SessionConfigured` - Session initialization complete
- `TaskStarted` - Agent begins processing a task
- `TaskComplete` - Agent finishes all actions
- `TurnAborted` - Task was interrupted or failed
- `ShutdownComplete` - Agent is shutting down
- `TokenCount` - Token usage tracking updates

### Event Transport

Events are sent as MCP notifications (`codex/codex-rs/mcp-server/src/outgoing_message.rs:48-54`):

```json
{
  "jsonrpc": "2.0",
  "method": "codex/event",
  "params": {
    "id": "submission-123",
    "msg": {
      "type": "exec_command_output_delta",
      "call_id": "exec-456",
      "stream": "stdout",
      "chunk": "SGVsbG8gV29ybGQK"  // base64 encoded bytes
    }
  }
}
```

### Typical Event Flow

1. `SessionConfigured` - Session initialization
2. `TaskStarted` - Task begins
3. `AgentReasoningDelta` - AI thinking process (streaming)
4. `ExecCommandBegin` - Command starts
5. `ExecCommandOutputDelta` - Command output (real-time streaming)
6. `ExecCommandEnd` - Command completes
7. `AgentMessageDelta` - Final response (streaming)
8. `TaskComplete` - Task finished

## Complete Event Output Schemas

### Event Structure

**Core Event Container** (`codex/codex-rs/protocol/src/protocol.rs:418-451`):
```rust
pub struct Event {
    /// Submission ID that this event is correlated with
    pub id: String,
    /// Event payload
    pub msg: EventMsg,
}
```

**JSON Transport Format**:
```json
{
  "jsonrpc": "2.0",
  "method": "codex/event",
  "params": {
    "id": "submission-123",
    "msg": {
      "type": "event_type_name",
      // ... event-specific fields
    }
  }
}
```

### Complete EventMsg Enum (30+ Event Types)

**EventMsg Definition** (`codex/codex-rs/protocol/src/protocol.rs:418-519`):
```rust
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum EventMsg {
    // Task Management
    TaskStarted(TaskStartedEvent),
    TaskComplete(TaskCompleteEvent),
    TurnAborted(TurnAbortedEvent),

    // Agent Communication
    AgentMessage(AgentMessageEvent),
    AgentMessageDelta(AgentMessageDeltaEvent),
    UserMessage(UserMessageEvent),

    // Agent Reasoning
    AgentReasoning(AgentReasoningEvent),
    AgentReasoningDelta(AgentReasoningDeltaEvent),
    AgentReasoningRawContent(AgentReasoningRawContentEvent),
    AgentReasoningRawContentDelta(AgentReasoningRawContentDeltaEvent),
    AgentReasoningSectionBreak(AgentReasoningSectionBreakEvent),

    // Session Management
    SessionConfigured(SessionConfiguredEvent),
    TokenCount(TokenCountEvent),

    // Command Execution
    ExecCommandBegin(ExecCommandBeginEvent),
    ExecCommandOutputDelta(ExecCommandOutputDeltaEvent),
    ExecCommandEnd(ExecCommandEndEvent),

    // Approval Requests
    ExecApprovalRequest(ExecApprovalRequestEvent),
    ApplyPatchApprovalRequest(ApplyPatchApprovalRequestEvent),

    // Tool Invocations
    McpToolCallBegin(McpToolCallBeginEvent),
    McpToolCallEnd(McpToolCallEndEvent),
    WebSearchBegin(WebSearchBeginEvent),
    WebSearchEnd(WebSearchEndEvent),

    // Patch Operations
    PatchApplyBegin(PatchApplyBeginEvent),
    PatchApplyEnd(PatchApplyEndEvent),

    // System Events
    Error(ErrorEvent),
    StreamError(StreamErrorEvent),
    BackgroundEvent(BackgroundEventEvent),
    ShutdownComplete,

    // ... and more
}
```

### Detailed Event Schemas by Category

#### 1. Task Management Events

**TaskStartedEvent**:
```json
{
  "type": "task_started",
  "model_context_window": 128000
}
```
```rust
pub struct TaskStartedEvent {
    pub model_context_window: Option<u64>,
}
```

**TaskCompleteEvent**:
```json
{
  "type": "task_complete",
  "last_agent_message": "I've successfully implemented the requested functionality."
}
```
```rust
pub struct TaskCompleteEvent {
    pub last_agent_message: Option<String>,
}
```

**TurnAbortedEvent**:
```json
{
  "type": "turn_aborted",
  "reason": "interrupted"
}
```
```rust
pub struct TurnAbortedEvent {
    pub reason: TurnAbortReason,
}

pub enum TurnAbortReason {
    Interrupted,
    Replaced,
    ReviewEnded,
}
```

#### 2. Agent Communication Events

**AgentMessageEvent**:
```json
{
  "type": "agent_message",
  "message": "I'll help you implement a factorial function with error handling."
}
```

**AgentMessageDeltaEvent** (streaming):
```json
{
  "type": "agent_message_delta",
  "delta": "I'll help you "
}
```

**UserMessageEvent**:
```json
{
  "type": "user_message",
  "message": "Create a Python factorial function",
  "kind": "plain",
  "images": ["base64-encoded-image-data"]
}
```
```rust
pub struct UserMessageEvent {
    pub message: String,
    pub kind: Option<InputMessageKind>,
    pub images: Option<Vec<String>>,
}

pub enum InputMessageKind {
    Plain,
    UserInstructions,
    EnvironmentContext,
}
```

#### 3. Agent Reasoning Events

**AgentReasoningEvent**:
```json
{
  "type": "agent_reasoning",
  "text": "I need to create a factorial function that handles edge cases like negative numbers and zero."
}
```

**AgentReasoningDeltaEvent** (streaming):
```json
{
  "type": "agent_reasoning_delta",
  "delta": "I need to create a factorial "
}
```

**AgentReasoningRawContentEvent**:
```json
{
  "type": "agent_reasoning_raw_content",
  "text": "The user wants a factorial function. I should implement proper error handling for edge cases..."
}
```

**AgentReasoningSectionBreakEvent**:
```json
{
  "type": "agent_reasoning_section_break"
}
```

#### 4. Session Management Events

**SessionConfiguredEvent**:
```json
{
  "type": "session_configured",
  "session_id": "67e55044-10b1-426f-9247-bb680e5fe0c8",
  "model": "gpt-4o",
  "reasoning_effort": "medium",
  "history_log_id": 1234567,
  "history_entry_count": 42,
  "rollout_path": "/tmp/codex-session.jsonl",
  "initial_messages": null
}
```
```rust
pub struct SessionConfiguredEvent {
    pub session_id: ConversationId,
    pub model: String,
    pub reasoning_effort: Option<ReasoningEffortConfig>,
    pub history_log_id: u64,
    pub history_entry_count: usize,
    pub initial_messages: Option<Vec<EventMsg>>,
    pub rollout_path: PathBuf,
}
```

**TokenCountEvent**:
```json
{
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
      "input_tokens": 150,
      "cached_input_tokens": 50,
      "output_tokens": 80,
      "reasoning_output_tokens": 20,
      "total_tokens": 230
    },
    "model_context_window": 128000
  }
}
```
```rust
pub struct TokenCountEvent {
    pub info: Option<TokenUsageInfo>,
}

pub struct TokenUsageInfo {
    pub total_token_usage: TokenUsage,
    pub last_token_usage: TokenUsage,
    pub model_context_window: Option<u64>,
}

pub struct TokenUsage {
    pub input_tokens: u64,
    pub cached_input_tokens: u64,
    pub output_tokens: u64,
    pub reasoning_output_tokens: u64,
    pub total_tokens: u64,
}
```

#### 5. Command Execution Events

**ExecCommandBeginEvent**:
```json
{
  "type": "exec_command_begin",
  "call_id": "exec-789",
  "command": ["python", "-m", "pytest", "test_factorial.py"],
  "cwd": "/home/user/project",
  "parsed_cmd": [{"kind": "literal", "value": "python"}]
}
```
```rust
pub struct ExecCommandBeginEvent {
    pub call_id: String,
    pub command: Vec<String>,
    pub cwd: PathBuf,
    pub parsed_cmd: Vec<ParsedCommand>,
}
```

**ExecCommandOutputDeltaEvent** (real-time streaming):
```json
{
  "type": "exec_command_output_delta",
  "call_id": "exec-789",
  "stream": "stdout",
  "chunk": "SGVsbG8gV29ybGQK"
}
```
```rust
pub struct ExecCommandOutputDeltaEvent {
    pub call_id: String,
    pub stream: ExecOutputStream,
    pub chunk: Vec<u8>,  // base64 encoded in JSON
}

pub enum ExecOutputStream {
    Stdout,
    Stderr,
}
```

**ExecCommandEndEvent**:
```json
{
  "type": "exec_command_end",
  "call_id": "exec-789",
  "stdout": "===== test session starts =====\n1 passed in 0.05s",
  "stderr": "",
  "aggregated_output": "===== test session starts =====\n1 passed in 0.05s",
  "exit_code": 0,
  "duration": "0.05s",
  "formatted_output": "Command executed successfully."
}
```
```rust
pub struct ExecCommandEndEvent {
    pub call_id: String,
    pub stdout: String,
    pub stderr: String,
    pub aggregated_output: String,
    pub exit_code: i32,
    pub duration: Duration,
    pub formatted_output: String,
}
```

#### 6. Approval Request Events

**ExecApprovalRequestEvent**:
```json
{
  "type": "exec_approval_request",
  "call_id": "exec-456",
  "command": ["rm", "-rf", "temp_files/"],
  "cwd": "/home/user/project",
  "reason": "Cleaning up temporary files"
}
```
```rust
pub struct ExecApprovalRequestEvent {
    pub call_id: String,
    pub command: Vec<String>,
    pub cwd: PathBuf,
    pub reason: Option<String>,
}
```

**ApplyPatchApprovalRequestEvent**:
```json
{
  "type": "apply_patch_approval_request",
  "call_id": "patch-123",
  "changes": {
    "/home/user/factorial.py": {
      "type": "add",
      "content": "def factorial(n):\n    if n < 0:\n        raise ValueError('Negative input')\n    return 1 if n <= 1 else n * factorial(n-1)"
    }
  },
  "reason": "Creating the factorial function with error handling",
  "grant_root": "/home/user/project"
}
```
```rust
pub struct ApplyPatchApprovalRequestEvent {
    pub call_id: String,
    pub changes: HashMap<PathBuf, FileChange>,
    pub reason: Option<String>,
    pub grant_root: Option<PathBuf>,
}

pub enum FileChange {
    Add { content: String },
    Delete { content: String },
    Update { unified_diff: String, move_path: Option<PathBuf> },
}
```

#### 7. Tool Invocation Events

**McpToolCallBeginEvent**:
```json
{
  "type": "mcp_tool_call_begin",
  "call_id": "mcp-456",
  "invocation": {
    "server": "web-search",
    "tool": "search",
    "arguments": {"query": "Python factorial implementation best practices"}
  }
}
```

**McpToolCallEndEvent**:
```json
{
  "type": "mcp_tool_call_end",
  "call_id": "mcp-456",
  "invocation": {
    "server": "web-search",
    "tool": "search",
    "arguments": {"query": "Python factorial implementation best practices"}
  },
  "duration": "2.3s",
  "result": {
    "Ok": {
      "content": [{"type": "text", "text": "Found 10 relevant results..."}],
      "is_error": false
    }
  }
}
```
```rust
pub struct McpToolCallBeginEvent {
    pub call_id: String,
    pub invocation: McpInvocation,
}

pub struct McpToolCallEndEvent {
    pub call_id: String,
    pub invocation: McpInvocation,
    pub duration: Duration,
    pub result: Result<CallToolResult, String>,
}

pub struct McpInvocation {
    pub server: String,
    pub tool: String,
    pub arguments: Option<serde_json::Value>,
}
```

#### 8. System Events

**ErrorEvent**:
```json
{
  "type": "error",
  "message": "Failed to execute command: permission denied"
}
```

**StreamErrorEvent**:
```json
{
  "type": "stream_error",
  "message": "Connection to model interrupted, retrying..."
}
```

**BackgroundEventEvent**:
```json
{
  "type": "background_event",
  "message": "Session cleanup completed"
}
```

**ShutdownComplete**:
```json
{
  "type": "shutdown_complete"
}
```

### Serialization Details & Transport

#### Serde Attributes Used

**Core Serialization**:
- `#[derive(Debug, Clone, Deserialize, Serialize)]` - Standard JSON serialization
- `#[serde(tag = "type", rename_all = "snake_case")]` - Externally tagged enum with snake_case field names
- `#[serde(skip_serializing_if = "Option::is_none")]` - Skip None values in JSON output

**Special Field Handling**:
- `#[serde_as(as = "serde_with::base64::Base64")]` - Base64 encoding for binary data (like `ExecCommandOutputDeltaEvent.chunk`)
- `#[ts(type = "string")]` - TypeScript type override for Rust types like `Duration`
- `#[serde(default)]` - Use default value when deserializing missing fields

#### Binary Data Encoding

**Command Output Chunks**: Raw bytes in `ExecCommandOutputDeltaEvent.chunk` are base64 encoded:
```rust
// Rust: Vec<u8> with raw bytes
pub chunk: Vec<u8>

// JSON: base64 encoded string
"chunk": "SGVsbG8gV29ybGQK"  // "Hello World\n"
```

#### Duration Serialization

**Duration Fields**: Rust `Duration` types are serialized as human-readable strings:
```rust
// Rust: std::time::Duration
pub duration: Duration

// JSON: string format
"duration": "2.3s"
```

### Event Correlation & Transport Format

#### Complete MCP Notification Structure

**Full Event Notification** (`codex/codex-rs/mcp-server/src/outgoing_message.rs:48-54`):
```json
{
  "jsonrpc": "2.0",
  "method": "codex/event",
  "params": {
    "meta": {
      "timestamp": "2025-01-15T10:30:45Z",
      "session_info": {
        "conversation_id": "67e55044-10b1-426f-9247-bb680e5fe0c8",
        "model": "gpt-4o"
      }
    },
    "event": {
      "id": "submission-123",
      "msg": {
        "type": "exec_command_output_delta",
        "call_id": "exec-789",
        "stream": "stdout",
        "chunk": "VGVzdCBwYXNzZWQh"
      }
    }
  }
}
```

#### Event Correlation Patterns

**Submission Correlation**: All events include `id` field linking to originating user request:
```json
{
  "id": "submission-123",  // Links back to original tool call
  "msg": { /* event payload */ }
}
```

**Call Correlation**: Related events share `call_id` for operation tracking:
```json
// Command execution sequence
{"type": "exec_command_begin", "call_id": "exec-789", ...}
{"type": "exec_command_output_delta", "call_id": "exec-789", ...}
{"type": "exec_command_output_delta", "call_id": "exec-789", ...}
{"type": "exec_command_end", "call_id": "exec-789", ...}
```

**Event Pairing**: Many operations have Begin/End pairs for progress tracking:
- `ExecCommandBegin` ↔ `ExecCommandEnd`
- `McpToolCallBegin` ↔ `McpToolCallEnd`
- `PatchApplyBegin` ↔ `PatchApplyEnd`
- `WebSearchBegin` ↔ `WebSearchEnd`

#### Streaming Event Patterns

**Delta Streaming**: Incremental content delivery:
```json
// Reasoning stream
{"type": "agent_reasoning_delta", "delta": "I need to "}
{"type": "agent_reasoning_delta", "delta": "analyze the "}
{"type": "agent_reasoning_delta", "delta": "requirements..."}

// Message stream
{"type": "agent_message_delta", "delta": "Here's the "}
{"type": "agent_message_delta", "delta": "implementation:"}
```

**Output Streaming**: Real-time command output:
```json
{"type": "exec_command_output_delta", "call_id": "exec-123", "stream": "stdout", "chunk": "UnVubmluZyB0ZXN0cw=="}
{"type": "exec_command_output_delta", "call_id": "exec-123", "stream": "stdout", "chunk": "LgoKVGVzdCBzdWl0ZQ=="}
```

#### Performance & Rate Limiting

**Delta Limiting**: System caps output delta events to prevent client overload:
- Maximum deltas per command execution (`MAX_EXEC_OUTPUT_DELTAS_PER_CALL`)
- Automatic buffering and chunking for high-volume output
- Graceful degradation when rate limits exceeded

**Channel Buffering**: Async channels provide high throughput:
- Bounded channels with configurable capacity (`CHANNEL_CAPACITY`)
- Non-blocking event emission
- Backpressure handling for slow consumers

## Tool Information

### Tool 1: `mcp__codex__codex`

**Purpose**: Run a new Codex session with configurable parameters.
**Implementation**: `codex/codex-rs/mcp-server/src/codex_tool_config.rs:102-131`

#### Complete JSON Schema

```json
{
  "type": "object",
  "properties": {
    "prompt": {
      "description": "The *initial user prompt* to start the Codex conversation.",
      "type": "string"
    },
    "model": {
      "description": "Optional override for the model name (e.g. \"o3\", \"o4-mini\").",
      "type": "string"
    },
    "approval-policy": {
      "description": "Approval policy for shell commands generated by the model: `untrusted`, `on-failure`, `on-request`, `never`.",
      "enum": ["untrusted", "on-failure", "on-request", "never"],
      "type": "string"
    },
    "sandbox": {
      "description": "Sandbox mode: `read-only`, `workspace-write`, or `danger-full-access`.",
      "enum": ["read-only", "workspace-write", "danger-full-access"],
      "type": "string"
    },
    "cwd": {
      "description": "Working directory for the session. If relative, it is resolved against the server process's current working directory.",
      "type": "string"
    },
    "profile": {
      "description": "Configuration profile from config.toml to specify default options.",
      "type": "string"
    },
    "config": {
      "description": "Individual config settings that will override what is in CODEX_HOME/config.toml.",
      "additionalProperties": true,
      "type": "object"
    },
    "base-instructions": {
      "description": "The set of instructions to use instead of the default ones.",
      "type": "string"
    },
    "include-plan-tool": {
      "description": "Whether to include the plan tool in the conversation.",
      "type": "boolean"
    }
  },
  "required": ["prompt"]
}
```

#### Parameter Details

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | ✅ | The initial user prompt to start the Codex conversation |
| `model` | string | ❌ | Optional model override (e.g., "o3", "o4-mini") |
| `sandbox` | enum | ❌ | Sandbox mode: `read-only`, `workspace-write`, or `danger-full-access` |
| `approval-policy` | enum | ❌ | Shell command approval: `untrusted`, `on-failure`, `on-request`, `never` |
| `cwd` | string | ❌ | Working directory (relative paths resolved against server process CWD) |
| `config` | object | ❌ | Individual config settings overriding CODEX_HOME/config.toml |
| `profile` | string | ❌ | Configuration profile from config.toml for default options |
| `base-instructions` | string | ❌ | Custom instruction set instead of defaults |
| `include-plan-tool` | boolean | ❌ | Whether to include the plan tool in conversation |

#### Sandbox Modes

- **`read-only`**: Maximum safety, no file modifications allowed
- **`workspace-write`**: Balanced approach, allows workspace modifications
- **`danger-full-access`**: Full system access (use with extreme caution)

#### Approval Policies

- **`untrusted`**: Require approval for all shell commands
- **`on-failure`**: Approve on command failure
- **`on-request`**: Approve when explicitly requested
- **`never`**: Never require approval (automatic execution)

#### Output

Returns a comprehensive response containing:
- Generated code and explanations
- Execution results
- Session metadata
- **Conversation ID for continuation**

#### Real-time Event Streaming

**Event Streaming**: ✅ **Full real-time event streaming supported**
- Live AI reasoning and response generation
- Real-time command execution output
- Progress notifications and status updates
- Interactive approval requests when needed

**Event Types During Execution**:
- `SessionConfigured` → `TaskStarted` → `AgentReasoningDelta` (streaming) → `ExecCommandBegin` → `ExecCommandOutputDelta` (streaming) → `ExecCommandEnd` → `AgentMessageDelta` (streaming) → `TaskComplete`

---

### Tool 2: `mcp__codex__codex-reply`

**Purpose**: Continue an existing Codex conversation with additional prompts.
**Implementation**: `codex/codex-rs/mcp-server/src/codex_tool_config.rs:193-222`

#### Complete JSON Schema

```json
{
  "type": "object",
  "properties": {
    "conversationId": {
      "description": "The conversation id for this Codex session.",
      "type": "string"
    },
    "prompt": {
      "description": "The *next user prompt* to continue the Codex conversation.",
      "type": "string"
    }
  },
  "required": ["conversationId", "prompt"]
}
```

#### Parameter Details

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conversationId` | string | ✅ | The conversation ID from initial Codex session |
| `prompt` | string | ✅ | The next user prompt to continue the conversation |

#### Output

Returns continuation response containing:
- Additional generated code
- Updated explanations
- Execution results from new prompt
- **Maintained conversation context**

#### Real-time Event Streaming

**Event Streaming**: ✅ **Full real-time event streaming supported**
- Continues existing session with full event visibility
- Same event types as initial `codex` tool
- Maintains conversation state across multiple replies

## Technical Architecture

### Implementation Files

- **CLI Command Handler**: `codex/codex-rs/cli/src/mcp_cmd.rs:5-47`
- **MCP Server Core**: `codex/codex-rs/mcp-server/src/lib.rs:79-123`
- **Tool Configuration**: `codex/codex-rs/mcp-server/src/codex_tool_config.rs`
- **Message Processor**: `codex/codex-rs/mcp-server/src/message_processor.rs:315-361`
- **Event Protocol**: `codex/codex-rs/protocol/src/protocol.rs:419-451`
- **Event Transport**: `codex/codex-rs/mcp-server/src/outgoing_message.rs:48-54`

### Submission Queue / Event Queue Pattern

The system uses an **async channel-based architecture**:
- **Incoming Channel**: Receives MCP JSON-RPC requests
- **Outgoing Channel**: Sends responses and event notifications
- **Background Tasks**: Process messages concurrently using Tokio
- **Event Correlation**: Links events to originating requests via submission IDs

### Session Management

**Conversation Manager** (`ConversationManager`):\n- Maintains session state across multiple tool calls\n- Assigns unique conversation IDs\n- Handles session interruption and cleanup\n- Manages background task lifecycle

## Usage Examples

### Example 1: Basic Codex Session with Event Streaming

```json
{
  "tool": "mcp__codex__codex",
  "parameters": {
    "prompt": "Create a Python function that calculates the factorial of a number with error handling",
    "sandbox": "workspace-write",
    "approval-policy": "on-request"
  }
}
```

**Expected Event Flow**:
1. `SessionConfigured` - Setup complete
2. `TaskStarted` - AI begins work
3. `AgentReasoningDelta` - "I'll create a factorial function with proper error handling..."
4. `AgentMessageDelta` - "Here's a robust factorial implementation..."
5. `ExecCommandBegin` - Running tests
6. `ExecCommandOutputDelta` - Real-time test output
7. `ExecCommandEnd` - Tests complete
8. `TaskComplete` - Session finished

### Example 2: Advanced Configuration with Full Access

```json
{
  "tool": "mcp__codex__codex",
  "parameters": {
    "prompt": "Build a REST API with FastAPI for user management",
    "model": "o3",
    "sandbox": "workspace-write",
    "cwd": "./api-project",
    "approval-policy": "untrusted",
    "include-plan-tool": true,
    "config": {
      "max_tokens": 4000,
      "temperature": 0.7
    }
  }
}
```

**Key Events**:
- `ExecApprovalRequest` - Permission requests for commands
- `PatchApplyBegin/End` - File modification events
- `McpToolCallBegin/End` - External tool usage

### Example 3: Interactive Conversation Continuation

```json
{
  "tool": "mcp__codex__codex-reply",
  "parameters": {
    "conversationId": "conv_abc123",
    "prompt": "Now add authentication middleware to the API"
  }
}
```

**Session Continuity**: Maintains full context from previous interactions with continued event streaming.

### Example 4: Secure Read-Only Analysis

```json
{
  "tool": "mcp__codex__codex",
  "parameters": {
    "prompt": "Analyze this codebase for potential security vulnerabilities",
    "sandbox": "read-only",
    "approval-policy": "never"
  }
}
```

**Safety Features**: No file modifications, no command execution, pure analysis with reasoning events only.

## Security Considerations

- **Always start with restrictive sandbox modes** (`read-only` or `workspace-write`)
- **Use approval policies** to maintain control over shell command execution
- **Review generated code** before executing in production environments
- **Limit working directory scope** using the `cwd` parameter
- **Monitor conversation context** to prevent unintended actions in long sessions

## Troubleshooting

### Common Issues

#### Event Streaming Problems
- **Missing Events**: Check MCP client notification handling for `"codex/event"` method
- **Event Flooding**: Command output deltas are limited to prevent overwhelming clients
- **Correlation Issues**: Use `id` field to correlate events with originating requests

#### Tool Execution Issues
- **Approval Timeouts**: `ExecApprovalRequest` events require timely user responses
- **Sandbox Violations**: Commands blocked by sandbox mode will generate error events
- **Session Interruption**: Use `TurnAborted` events to detect failed operations

#### Configuration Problems
- **Invalid Profiles**: Non-existent profile names will cause initialization errors
- **Permission Denied**: Check file system permissions for `cwd` parameter
- **Model Availability**: Specified models must be available in the Codex installation

### Debugging Event Streams

**Enable Event Logging**: Monitor all `"codex/event"` notifications for debugging
**Check Event Correlation**: Match event `id` fields with tool call requests
**Validate Event Sequence**: Ensure proper `Begin`/`End` event pairing for commands

### Performance Optimization

- **Limit Output Deltas**: System automatically caps command output streaming
- **Use Appropriate Sandbox**: `read-only` mode for analysis, `workspace-write` for development
- **Configure Approval Policies**: `never` for trusted environments, `untrusted` for security

## Integration Notes

### MCP Client Integration
- **Event Handling**: Implement `"codex/event"` notification handlers for real-time updates
- **Session Persistence**: Store conversation IDs for multi-turn interactions
- **Approval Workflow**: Handle `ExecApprovalRequest` and `ApplyPatchApprovalRequest` events
- **Error Recovery**: Process `StreamError` and `TurnAborted` events gracefully

### Advanced Features
- **Conversation Continuity**: Sessions maintain state across multiple `codex-reply` calls
- **Configuration Profiles**: Standardize common setups via `profile` parameter
- **Custom Instructions**: Domain-specific behavior via `base-instructions` parameter
- **Planning Mode**: Complex multi-step projects with `include-plan-tool: true`

### Performance Considerations
- **Concurrent Sessions**: Each conversation ID represents an independent session
- **Resource Management**: Background tasks are cleaned up on session termination
- **Token Tracking**: Monitor `TokenCount` events for usage optimization
- **Stream Buffering**: Events use async channels for optimal throughput