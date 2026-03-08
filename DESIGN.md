# Codex Client — Design Document

## Table of Contents

1. [Overview](#overview)
2. [Codex App-Server Protocol Reference](#codex-app-server-protocol-reference)
   - [Transport](#transport)
   - [Message Format](#message-format)
   - [Core Primitives](#core-primitives)
   - [Lifecycle](#lifecycle)
   - [Client Requests](#client-requests)
   - [Client Notifications](#client-notifications)
   - [Server Requests (Approvals & Input)](#server-requests-approvals--input)
   - [Server Notifications](#server-notifications)
   - [ThreadItem Types](#threaditem-types)
   - [UserInput Types](#userinput-types)
   - [Approval Decisions](#approval-decisions)
   - [Sandbox Policies](#sandbox-policies)
   - [Authentication Modes](#authentication-modes)
   - [Error Model](#error-model)
   - [Schema Statistics](#schema-statistics)
3. [SDK Architecture — Layered Design](#sdk-architecture--layered-design)
   - [Design Principles](#design-principles)
   - [Project Structure](#project-structure)
   - [Protocol Core](#protocol-core)
   - [Typed Protocol Client](#typed-protocol-client)
   - [Session Runtime](#session-runtime)
   - [Type Generation](#type-generation)
   - [Transport Abstraction](#transport-abstraction)
   - [Middleware System](#middleware-system)
   - [Testing Infrastructure](#testing-infrastructure)
4. [Implementation Plan](#implementation-plan)

---

## Overview

Codex Client is a TypeScript SDK that wraps the OpenAI Codex app-server protocol — the JSON-RPC 2.0 bidirectional interface that powers rich Codex clients (e.g., the VS Code extension). The goal is to provide an easy-to-use, layered abstraction for embedding Codex into custom products, building test harnesses, and automating agent workflows.

The SDK follows a three-tier architecture:

- **Protocol Core** — Raw protocol connection and JSON-RPC message flow
- **Typed Protocol Client** — Typed request/response surface with middleware and routing
- **Session Runtime** — High-level session/thread/turn object model

Users pick the abstraction level they need. Each layer is independently usable.

---

## Codex App-Server Protocol Reference

This section documents the full Codex app-server protocol as understood from the [official documentation](https://developers.openai.com/codex/app-server) and the 157 JSON schema files in `schema/`.

### Transport

The protocol supports two transports:

| Transport | Flag | Format | Notes |
|---|---|---|---|
| **stdio** (default) | `--listen stdio://` | Newline-delimited JSON (JSONL) | One JSON-RPC message per line |
| **WebSocket** (experimental) | `--listen ws://IP:PORT` | One JSON-RPC message per WebSocket text frame | Bounded ingress queue; rejects with code `-32001` when full |

The `"jsonrpc":"2.0"` header is **omitted on the wire** (unlike standard JSON-RPC 2.0).

### Message Format

Three message shapes:

**Request** (has `id`, expects response):
```json
{ "method": "thread/start", "id": 10, "params": { "model": "gpt-5.1-codex" } }
```

**Response** (echoes `id`):
```json
{ "id": 10, "result": { "thread": { "id": "thr_123" } } }
```
```json
{ "id": 10, "error": { "code": 123, "message": "Something went wrong" } }
```

**Notification** (no `id`, no response):
```json
{ "method": "turn/started", "params": { "turn": { "id": "turn_456" } } }
```

Requests may include an optional `trace` field for W3C distributed tracing (`traceparent`, `tracestate`).

### Core Primitives

```
Thread (conversation)
 └── Turn (single user request + agent work)
      └── Item (unit of I/O: message, command, file change, tool call, etc.)
```

- **Thread**: A conversation between a user and the Codex agent. Has `id`, `name`, `preview`, `status`, `ephemeral`, `modelProvider`, `createdAt`, `updatedAt`. Status is one of `notLoaded`, `idle`, `systemError`, or `active` (with `activeFlags` like `waitingOnApproval`).
- **Turn**: A single user request and the agent work that follows. Has `id`, `status` (`inProgress`, `completed`, `interrupted`, `failed`), `items[]`, and `error`.
- **Item**: A discriminated union (`ThreadItem`) — see [ThreadItem Types](#threaditem-types).

### Lifecycle

```
Client                                           Server
  │                                                │
  │──── initialize (id:0) ────────────────────────>│
  │<─── response (id:0, result: {userAgent}) ──────│
  │──── initialized (notification) ───────────────>│
  │                                                │
  │──── thread/start (id:1) ──────────────────────>│
  │<─── response (id:1, result: {thread}) ─────────│
  │<─── thread/started (notification) ─────────────│
  │                                                │
  │──── turn/start (id:2) ────────────────────────>│
  │<─── response (id:2, result: {turn}) ───────────│
  │<─── turn/started (notification) ───────────────│
  │                                                │
  │<─── item/started (notification) ───────────────│
  │<─── item/agentMessage/delta (notification) ────│  (repeated)
  │<─── item/completed (notification) ─────────────│
  │                                                │
  │     [if approval needed]                       │
  │<─── item/commandExecution/requestApproval ─────│  (server request, has id)
  │──── response (id:N, decision: accept) ────────>│
  │<─── serverRequest/resolved (notification) ─────│
  │                                                │
  │<─── turn/completed (notification) ─────────────│
  │                                                │
  │──── thread/archive (id:3) ────────────────────>│
  │<─── response (id:3, result: {}) ───────────────│
  │<─── thread/archived (notification) ────────────│
```

**Key rules:**
- `initialize` must be the first request on every connection. Repeated calls return `Already initialized`.
- `initialized` notification must follow the `initialize` response.
- Requests before initialization receive `Not initialized` error.
- `thread/start` auto-subscribes the connection to turn/item events for that thread.
- `turn/start` can override model, effort, personality, `cwd`, sandbox policy, and `outputSchema` per turn. These become defaults for later turns on the same thread (except `outputSchema` which is turn-scoped).

### Client Requests

All requests the client can send to the server:

#### Initialization
| Method | Params | Response | Notes |
|---|---|---|---|
| `initialize` | `clientInfo: {name, title?, version}`, `capabilities?: {experimentalApi?, optOutNotificationMethods?}` | `{userAgent}` | Must be first request |

#### Thread Management
| Method | Params | Response | Notes |
|---|---|---|---|
| `thread/start` | `model?`, `cwd?`, `approvalPolicy?`, `sandbox?`, `personality?`, `serviceName?`, `dynamicTools?` (experimental) | `{thread}` | Creates new thread |
| `thread/resume` | `threadId`, `personality?`, + same overrides as start | `{thread}` | Continues existing thread |
| `thread/fork` | `threadId` | `{thread}` | Branches thread with new id |
| `thread/read` | `threadId`, `includeTurns?` | `{thread}` | Read without subscribing |
| `thread/list` | `cursor?`, `limit?`, `sortKey?`, `modelProviders?`, `sourceKinds?`, `archived?`, `cwd?` | `{data: Thread[], nextCursor}` | Cursor-paginated |
| `thread/loaded/list` | (none) | `{data: string[]}` | Thread ids in memory |
| `thread/archive` | `threadId` | `{}` | Moves log to archive dir |
| `thread/unarchive` | `threadId` | `{thread}` | Restores from archive |
| `thread/unsubscribe` | `threadId` | `{status}` | `unsubscribed`, `notSubscribed`, or `notLoaded` |
| `thread/compact/start` | `threadId` | `{}` | Triggers compaction async |
| `thread/rollback` | `threadId`, `numTurns` | `{thread}` | Drops last N turns |
| `thread/name/set` | `threadId`, `name` | `{thread}` | Set thread title |
| `thread/metadata/update` | `threadId`, `gitInfo?` | `{}` | Update thread metadata |

**`sourceKinds` values:** `cli`, `vscode`, `exec`, `appServer`, `subAgent`, `subAgentReview`, `subAgentCompact`, `subAgentThreadSpawn`, `subAgentOther`, `unknown`

#### Turn Management
| Method | Params | Response | Notes |
|---|---|---|---|
| `turn/start` | `threadId`, `input: UserInput[]`, `cwd?`, `approvalPolicy?`, `sandboxPolicy?`, `model?`, `effort?`, `summary?`, `personality?`, `outputSchema?`, `collaborationMode?` | `{turn}` | Begin agent work |
| `turn/steer` | `threadId`, `input: UserInput[]`, `expectedTurnId` | `{turnId}` | Append input to active turn |
| `turn/interrupt` | `threadId`, `turnId` | `{}` | Cancel in-flight turn |

#### Review
| Method | Params | Response | Notes |
|---|---|---|---|
| `review/start` | `threadId`, `delivery: "inline"|"detached"`, `target: {type, ...}` | `{turn, reviewThreadId}` | Review targets: `uncommittedChanges`, `baseBranch`, `commit`, `custom` |

#### Command Execution
| Method | Params | Response | Notes |
|---|---|---|---|
| `command/exec` | `command: string[]`, `cwd?`, `sandboxPolicy?`, `timeoutMs?` | `{exitCode, stdout, stderr}` | Standalone, no thread |

#### Model & Features
| Method | Params | Response | Notes |
|---|---|---|---|
| `model/list` | `limit?`, `includeHidden?` | `{data: Model[], nextCursor}` | Each model has `supportedReasoningEfforts`, `inputModalities`, etc. |
| `experimentalFeature/list` | `limit?` | `{data: Feature[], nextCursor}` | Stage: `beta`, `underDevelopment`, `stable`, `deprecated`, `removed` |
| `collaborationMode/list` | (none) | `{data}` | Experimental, no pagination |

#### Skills
| Method | Params | Response | Notes |
|---|---|---|---|
| `skills/list` | `cwds?`, `forceReload?`, `perCwdExtraUserRoots?` | `{data: [{cwd, skills[], errors[]}]}` | Skills have `interface`, `dependencies` |
| `skills/config/write` | `path`, `enabled` | `{}` | Enable/disable by path |
| `skills/remote/read` | (params) | (response) | Remote skill info |
| `skills/remote/write` | (params) | (response) | Persist remote skills |

#### Apps (Connectors)
| Method | Params | Response | Notes |
|---|---|---|---|
| `app/list` | `cursor?`, `limit?`, `threadId?`, `forceRefetch?` | `{data: App[], nextCursor}` | Each app has `isAccessible`, `isEnabled` |

#### Configuration
| Method | Params | Response | Notes |
|---|---|---|---|
| `config/read` | `includeLayers?` | `{config}` | Resolved effective config |
| `config/value/write` | `keyPath`, `value`, `mergeStrategy` | `{}` | Write single key to `config.toml` |
| `config/batchWrite` | `edits: [{keyPath, value, mergeStrategy}]` | `{}` | Atomic batch write |
| `configRequirements/read` | `{}` | `{requirements}` | Admin requirements from `requirements.toml`/MDM |
| `config/mcpServer/reload` | (none) | (response) | Reload MCP server config |

#### Authentication & Account
| Method | Params | Response | Notes |
|---|---|---|---|
| `account/read` | `refreshToken?` | `{account, requiresOpenaiAuth}` | Check auth state |
| `account/login/start` | `type: "apiKey"|"chatgpt"|"chatgptAuthTokens"`, + type-specific fields | Type-specific result | `apiKey`: immediate, `chatgpt`: returns `authUrl`, `chatgptAuthTokens`: immediate |
| `account/login/cancel` | `loginId` | (notification emitted) | Cancel pending ChatGPT login |
| `account/logout` | (none) | `{}` | Sign out |
| `account/rateLimits/read` | (none) | `{rateLimits, rateLimitsByLimitId?}` | ChatGPT rate limits |

#### MCP Server
| Method | Params | Response | Notes |
|---|---|---|---|
| `mcpServerStatus/list` | `cursor?`, `limit?` | `{data, nextCursor}` | Server, tool, resource, auth status |
| `mcpServer/oauth/login` | `name` | `{authorizationUrl}` | Start OAuth for MCP server |

#### External Agent Config
| Method | Params | Response | Notes |
|---|---|---|---|
| `externalAgentConfig/detect` | `includeHome?`, `cwds?` | `{items}` | Detect migratable artifacts |
| `externalAgentConfig/import` | `migrationItems` | `{}` | Apply selected migrations |

#### Other
| Method | Params | Response | Notes |
|---|---|---|---|
| `feedback/upload` | `classification`, `reason?`, `conversationId?`, `extraLogFiles?` | (response) | Submit feedback |
| `fuzzyFileSearch` | `query`, `cwd`, `sessionId?` | `{files}` | Experimental |
| `windowsSandbox/setupStart` | `mode: "elevated"|"unelevated"` | `{started}` | Windows only |

### Client Notifications

| Method | Notes |
|---|---|
| `initialized` | Must follow `initialize` response |

### Server Requests (Approvals & Input)

These are JSON-RPC requests **from the server to the client** (they have an `id` and expect a response).

| Method | Params | Expected Response | Notes |
|---|---|---|---|
| `item/commandExecution/requestApproval` | `itemId`, `threadId`, `turnId`, `reason?`, `command?`, `cwd?`, `commandActions?`, `proposedExecpolicyAmendment?`, `networkApprovalContext?`, `availableDecisions?`, `additionalPermissions?` (experimental) | `{decision}` | See [Approval Decisions](#approval-decisions) |
| `item/fileChange/requestApproval` | `itemId`, `threadId`, `turnId`, `reason?`, `grantRoot?` | `{decision}` | See [Approval Decisions](#approval-decisions) |
| `item/tool/requestUserInput` | `threadId`, `turnId`, `toolCallId`, `questions[]` | `{answers}` | Questions can set `isOther` for free-form |
| `item/tool/call` | `threadId`, `turnId`, `tool`, `arguments` | `{contentItems}` | Dynamic tool call for client execution |
| `mcpServer/elicitation/request` | (params) | (response) | MCP server elicitation |
| `account/chatgptAuthTokens/refresh` | `reason`, `previousAccountId` | `{idToken, accessToken}` | Refresh external ChatGPT tokens |

**Legacy (v1) server requests:**
| Method | Params | Expected Response |
|---|---|---|
| `applyPatchApproval` | `command`, `cwd?` | `{decision}` |
| `execCommandApproval` | `command: string[]`, `cwd` | `{approved}` |

### Server Notifications

Notifications from the server to the client (no `id`, no response expected).

#### Thread Lifecycle
| Method | Params |
|---|---|
| `thread/started` | `{thread}` |
| `thread/status/changed` | `{threadId, status}` |
| `thread/closed` | `{threadId}` |
| `thread/archived` | `{threadId}` |
| `thread/unarchived` | `{threadId}` |
| `thread/name/updated` | `{threadId, name}` |
| `thread/tokenUsage/updated` | `{threadId, ...usage}` |
| `thread/compacted` | `{threadId}` (deprecated, use `contextCompaction` item) |

#### Turn Lifecycle
| Method | Params |
|---|---|
| `turn/started` | `{turn}` (status: `inProgress`, items: `[]`) |
| `turn/completed` | `{turn}` (status: `completed`/`interrupted`/`failed`, with `error?`) |
| `turn/diff/updated` | `{threadId, turnId, diff}` |
| `turn/plan/updated` | `{turnId, explanation?, plan: [{step, status}]}` |

#### Item Lifecycle
| Method | Params |
|---|---|
| `item/started` | `{item}` (full ThreadItem when work begins) |
| `item/completed` | `{item}` (final authoritative state) |

#### Item Deltas (Streaming)
| Method | Params | Notes |
|---|---|---|
| `item/agentMessage/delta` | `{itemId, delta}` | Streamed agent text |
| `item/plan/delta` | `{itemId, delta}` | Streamed plan text |
| `item/reasoning/textDelta` | `{itemId, delta}` | Raw reasoning text |
| `item/reasoning/summaryTextDelta` | `{itemId, delta, summaryIndex}` | Readable reasoning summaries |
| `item/reasoning/summaryPartAdded` | `{itemId}` | New summary section boundary |
| `item/commandExecution/outputDelta` | `{itemId, delta}` | Streamed stdout/stderr |
| `item/fileChange/outputDelta` | `{itemId, delta}` | apply_patch tool call response |
| `item/mcpToolCall/progress` | `{itemId, ...progress}` | MCP tool execution progress |

#### State & System
| Method | Params |
|---|---|
| `error` | `{error: {message, codexErrorInfo?, additionalDetails?}}` |
| `serverRequest/resolved` | `{threadId, requestId}` |
| `skills/changed` | `{}` |
| `account/updated` | `{authMode}` |
| `account/login/completed` | `{loginId, success, error?}` |
| `account/rateLimits/updated` | `{rateLimits}` |
| `app/list/updated` | `{data: App[]}` |
| `config/warning` | `{...warning}` |
| `model/rerouted` | `{...details}` |
| `deprecation/notice` | `{...notice}` |
| `context/compacted` | `{threadId}` |

#### Realtime (Experimental)
| Method | Params |
|---|---|
| `thread/realtime/started` | `{threadId}` |
| `thread/realtime/closed` | `{threadId}` |
| `thread/realtime/error` | `{threadId, error}` |
| `thread/realtime/itemAdded` | `{threadId, item}` |
| `thread/realtime/outputAudioDelta` | `{threadId, delta}` |

#### Fuzzy File Search (Experimental)
| Method | Params |
|---|---|
| `fuzzyFileSearch/sessionUpdated` | `{sessionId, query, files}` |
| `fuzzyFileSearch/sessionCompleted` | `{sessionId}` |

#### Platform-Specific
| Method | Params |
|---|---|
| `windowsSandbox/setupStarted` | `{mode}` |
| `windowsSandbox/setupCompleted` | `{mode, success, error?}` |
| `windowsWorldWritableWarning` | `{...details}` |
| `terminalInteraction` | `{...details}` |

### ThreadItem Types

`ThreadItem` is a discriminated union on the `type` field:

| Type | Key Fields | Notes |
|---|---|---|
| `userMessage` | `id`, `content: UserInput[]` | User text/image input, may include `textElements` for UI spans |
| `agentMessage` | `id`, `text`, `phase?` | Agent reply. `phase`: `commentary` or `final_answer` |
| `plan` | `id`, `text` | Proposed plan text (experimental) |
| `reasoning` | `id`, `summary`, `content` | Summary holds streamed summaries, content holds raw reasoning blocks |
| `commandExecution` | `id`, `command`, `cwd`, `status`, `commandActions`, `aggregatedOutput?`, `exitCode?`, `durationMs?` | Shell command execution |
| `fileChange` | `id`, `changes: [{path, kind, diff}]`, `status` | File edits. `kind`: `add`, `update`, `delete` |
| `mcpToolCall` | `id`, `server`, `tool`, `status`, `arguments`, `result?`, `error?` | MCP tool invocation |
| `dynamicToolCall` | `id`, `tool`, `arguments`, `status`, `contentItems?`, `success?`, `durationMs?` | Client-executed dynamic tool (experimental) |
| `collabAgentToolCall` | `id`, `tool`, `status`, `senderThreadId`, `receiverThreadId?`, `newThreadId?`, `prompt?`, `agentStatus?` | Multi-agent collaboration |
| `webSearch` | `id`, `query`, `action?` | Action type: `search`, `openPage`, `findInPage` |
| `imageView` | `id`, `path` | Agent viewed an image |
| `imageGeneration` | `id`, ... | Agent generated an image |
| `enteredReviewMode` | `id`, `review` | Reviewer started |
| `exitedReviewMode` | `id`, `review` | Reviewer finished, `review` has output text |
| `contextCompaction` | `id` | Conversation history compacted |

**Status values for command/file/tool items:** `inProgress`, `completed`, `failed`, `declined`

### UserInput Types

Discriminated union on `type`:

| Type | Fields | Notes |
|---|---|---|
| `text` | `text`, `textElements?` | Plain text, optional UI spans |
| `image` | `url` | URL-based image |
| `localImage` | `path` | Local file path image |
| `skill` | `name`, `path` | Skill invocation (recommended alongside `$<skill-name>` in text) |
| `mention` | `name`, `path` | App/connector mention (`app://<id>`) |

### Approval Decisions

**Command execution decisions:**
- `accept` — approve and run
- `acceptForSession` — approve for the rest of the session
- `decline` — reject the command
- `cancel` — cancel the turn
- `{ acceptWithExecpolicyAmendment: { execpolicy_amendment: string[] } }` — approve with exec policy amendment
- `{ applyNetworkPolicyAmendment: ... }` — approve with network policy amendment

**File change decisions:**
- `accept`
- `acceptForSession`
- `decline`
- `cancel`

### Sandbox Policies

| Type | Key Fields | Notes |
|---|---|---|
| `dangerFullAccess` | (none) | No sandbox restrictions |
| `readOnly` | `access?: ReadOnlyAccess` | Read-only. `access` defaults to `fullAccess` |
| `workspaceWrite` | `writableRoots?`, `readOnlyAccess?`, `networkAccess?: boolean` | Write within roots |
| `externalSandbox` | `networkAccess?: "restricted"|"enabled"` | Caller manages sandbox |

**ReadOnlyAccess:**
- `{ type: "fullAccess" }` — can read everything
- `{ type: "restricted", includePlatformDefaults: boolean, readableRoots: string[] }` — restricted read

### Authentication Modes

| Mode | `authMode` value | Login params | Notes |
|---|---|---|---|
| API Key | `"apikey"` | `{ type: "apiKey", apiKey: "sk-..." }` | Immediate |
| ChatGPT OAuth | `"chatgpt"` | `{ type: "chatgpt" }` | Returns `authUrl`, open in browser |
| External ChatGPT Tokens | `"chatgptAuthTokens"` | `{ type: "chatgptAuthTokens", idToken, accessToken }` | Host app manages tokens, server may request refresh |

### Error Model

Turn failures emit an `error` notification followed by `turn/completed` with `status: "failed"`.

**`codexErrorInfo` variants:**
| Variant | Notes |
|---|---|
| `ContextWindowExceeded` | Context too long |
| `UsageLimitExceeded` | Rate/quota limit hit |
| `HttpConnectionFailed` | Upstream 4xx/5xx (includes `httpStatusCode`) |
| `ResponseStreamConnectionFailed` | Stream connection error |
| `ResponseStreamDisconnected` | Stream disconnected mid-response |
| `ResponseTooManyFailedAttempts` | Retry limit exceeded |
| `BadRequest` | Invalid request |
| `Unauthorized` | Auth failure |
| `SandboxError` | Sandbox violation |
| `ServerOverloaded` | Server overloaded |
| `InternalServerError` | Internal error |
| `ThreadRollbackFailed` | Rollback operation failed |
| `Other` | Uncategorized |

### Schema Statistics

| Directory | Files | Description |
|---|---|---|
| `schema/` (root) | 34 | Core JSON-RPC types, approval params/responses, event messages |
| `schema/v1/` | 2 | Legacy `InitializeParams`, `InitializeResponse` |
| `schema/v2/` | 121 | Modern API: threads, turns, items, config, auth, skills, apps, notifications |
| **Total** | **157** | **410+ type definitions across all schemas** |

---

## SDK Architecture — Layered Design

### Design Principles

1. **Pick your level** — Three tiers (core, typed, runtime), each independently usable.
2. **Bottom-up composability** — Session Runtime is implemented in terms of Typed Protocol Client, which is implemented in terms of Protocol Core.
3. **Middleware for cross-cutting concerns** — Logging, recording/replay, auto-approval, metrics, auth token refresh — all implemented in Typed Protocol Client.
4. **Type safety from schemas** — TypeScript types auto-generated from the 157 JSON schema files. All layers share the same types.
5. **Testable without a server** — Mock transports, recording middleware, and replay transports enable full testing without a running Codex process.
6. **Minimal opinion at the bottom, maximum ergonomics at the top** — Protocol Core is zero-opinion. Session Runtime provides `thread.ask("fix the bug")` one-liners.

### Project Structure

```
codex-client/
├── schema/                          # JSON schema files (existing)
│   ├── v1/
│   ├── v2/
│   └── *.json
├── src/
│   ├── types/
│   │   ├── generated/               # Auto-generated from JSON schemas
│   │   │   ├── v1.ts
│   │   │   ├── v2.ts
│   │   │   ├── protocol.ts          # Core JSON-RPC types
│   │   │   └── index.ts
│   │   └── index.ts                 # Re-exports + hand-crafted convenience types
│   │
│   ├── transport/
│   │   ├── Transport.ts             # Transport interface
│   │   ├── StdioTransport.ts        # JSONL over child process stdio
│   │   ├── WebSocketTransport.ts    # WebSocket text frames
│   │   └── index.ts
│   │
│   ├── protocol-core/
│   │   ├── JsonRpcCodec.ts          # Parse/serialize JSON-RPC messages
│   │   ├── ProtocolConnection.ts    # Raw bidirectional message pump
│   │   └── index.ts
│   │
│   ├── protocol-client/
│   │   ├── TypedCodexClient.ts      # Typed methods for all client requests
│   │   ├── Middleware.ts            # Middleware interface & runner
│   │   ├── RequestRouter.ts         # Routes incoming messages to handlers
│   │   ├── IdGenerator.ts           # Request ID allocation
│   │   └── index.ts
│   │
│   ├── session-runtime/
│   │   ├── Session.ts               # Top-level entry point
│   │   ├── Thread.ts                # Thread object with methods
│   │   ├── Turn.ts                  # Turn as AsyncIterable<TurnEvent>
│   │   ├── TurnEvent.ts             # Discriminated union for turn events
│   │   ├── ApprovalPolicy.ts        # Interface + built-in policies
│   │   └── index.ts
│   │
│   ├── middleware/                   # Built-in middleware
│   │   ├── logging.ts               # Log all messages
│   │   ├── recording.ts             # Record messages for replay
│   │   ├── autoApproval.ts          # Auto-approve commands/files
│   │   └── index.ts
│   │
│   ├── testing/
│   │   ├── MockTransport.ts         # In-memory transport for unit tests
│   │   ├── ReplayTransport.ts       # Replay recorded protocol sessions
│   │   ├── fixtures.ts              # Factory functions for protocol messages
│   │   └── index.ts
│   │
│   └── index.ts                     # Main entry: re-exports all public API
│
├── scripts/
│   └── generate-types.ts            # Schema → TypeScript codegen
│
├── DESIGN.md                        # This file
├── package.json
└── tsconfig.json
```

### Protocol Core

Formerly "Layer 0". This tier owns byte/string transport boundaries, JSON-RPC framing, and raw message flow. It should stay small and unsurprising.

Zero-opinion bidirectional message pump. Parse JSONL, send/receive raw JSON-RPC objects.

#### `Transport` Interface

```ts
interface Transport {
  /** Send a raw string (one JSONL line or one WebSocket frame) */
  send(data: string): void;

  /** Incoming raw strings */
  [Symbol.asyncIterator](): AsyncIterator<string>;

  /** Close the transport */
  close(): Promise<void>;

  /** Emitted on transport-level errors */
  onError(handler: (error: Error) => void): void;
}
```

#### `ProtocolConnection`

```ts
class ProtocolConnection {
  constructor(transport: Transport);

  /** Send a raw JSON-RPC message object */
  send(msg: JsonRpcMessage): void;

  /** Async iterable of parsed incoming messages */
  get incoming(): AsyncIterable<JsonRpcMessage>;

  /** Close the connection */
  close(): Promise<void>;
}
```

#### Usage

```ts
import { ProtocolConnection, StdioTransport } from 'codex-client';

const conn = new ProtocolConnection(
  new StdioTransport({ command: 'codex', args: ['app-server'] })
);

conn.send({
  id: 1,
  method: 'initialize',
  params: { clientInfo: { name: 'debug-tool', version: '0.1' } },
});

for await (const msg of conn.incoming) {
  console.log(JSON.stringify(msg, null, 2));
  // Full manual control over every message
}
```

**Use cases:** Debugging, protocol sniffing, building completely custom clients, wrapping in other languages via FFI.

#### DO

- Keep the surface close to the wire format and protocol rules.
- Preserve message ordering and raw payload fidelity.
- Fail fast on malformed JSON-RPC frames and transport-level corruption.
- Expose primitives that higher tiers can compose without hidden state.

#### DON'T

- Don't add business workflow helpers here.
- Don't interpret protocol events into user-facing domain objects.
- Don't bake in approval policy, retries, or middleware concerns.
- Don't silently "fix" invalid server messages; surface them as errors.

#### Test Requirements

- Verify codec round-trips for request, response, and notification shapes.
- Verify omitted `jsonrpc` fields are accepted and emitted exactly as designed.
- Verify malformed frames fail deterministically with actionable errors.
- Verify transport close/error propagation reaches consumers without hangs.
- Verify message ordering is preserved under streaming input.

### Typed Protocol Client

Formerly "Layer 1". This tier owns typed request methods, request/response correlation, middleware, and dispatch for server requests and notifications.

Wraps `ProtocolConnection` with:
- Typed methods for every client request (auto-generated from schemas)
- Typed handlers for every server request and notification
- Middleware pipeline for cross-cutting concerns
- Automatic request ID management
- Pending request tracking with timeout

#### `TypedCodexClient`

```ts
class TypedCodexClient {
  constructor(transport: Transport);

  /** Install middleware */
  use(middleware: Middleware): this;

  // ── Client Requests (typed, return Promise) ──────────────────

  initialize(params: InitializeParams): Promise<InitializeResponse>;
  sendInitialized(): void;  // notification

  threadStart(params: ThreadStartParams): Promise<ThreadStartResponse>;
  threadResume(params: ThreadResumeParams): Promise<ThreadResumeResponse>;
  threadFork(params: ThreadForkParams): Promise<ThreadForkResponse>;
  threadRead(params: ThreadReadParams): Promise<ThreadReadResponse>;
  threadList(params: ThreadListParams): Promise<ThreadListResponse>;
  threadLoadedList(): Promise<ThreadLoadedListResponse>;
  threadArchive(params: ThreadArchiveParams): Promise<ThreadArchiveResponse>;
  threadUnarchive(params: ThreadUnarchiveParams): Promise<ThreadUnarchiveResponse>;
  threadUnsubscribe(params: ThreadUnsubscribeParams): Promise<ThreadUnsubscribeResponse>;
  threadCompactStart(params: ThreadCompactStartParams): Promise<{}>;
  threadRollback(params: ThreadRollbackParams): Promise<ThreadRollbackResponse>;

  turnStart(params: TurnStartParams): Promise<TurnStartResponse>;
  turnSteer(params: TurnSteerParams): Promise<TurnSteerResponse>;
  turnInterrupt(params: TurnInterruptParams): Promise<{}>;

  reviewStart(params: ReviewStartParams): Promise<ReviewStartResponse>;
  commandExec(params: CommandExecParams): Promise<CommandExecResponse>;
  modelList(params?: ModelListParams): Promise<ModelListResponse>;
  skillsList(params: SkillsListParams): Promise<SkillsListResponse>;
  appList(params?: AppsListParams): Promise<AppsListResponse>;
  configRead(params?: ConfigReadParams): Promise<ConfigReadResponse>;
  // ... all other methods

  // ── Server Request Handlers ──────────────────────────────────

  onServerRequest<M extends ServerRequestMethod>(
    method: M,
    handler: (params: ServerRequestParams<M>) => Promise<ServerRequestResult<M>>,
  ): this;

  // ── Server Notification Handlers ─────────────────────────────

  onNotification<M extends ServerNotificationMethod>(
    method: M,
    handler: (params: ServerNotificationParams<M>) => void,
  ): this;

  /** Remove all handlers for a method */
  off(method: string): this;

  /** Close the client and underlying transport */
  close(): Promise<void>;
}
```

#### Usage

```ts
import { TypedCodexClient, StdioTransport, loggingMiddleware } from 'codex-client';

const client = new TypedCodexClient(
  new StdioTransport({ command: 'codex', args: ['app-server'] })
);

// Middleware
client.use(loggingMiddleware({ level: 'debug' }));

// Initialize
await client.initialize({
  clientInfo: { name: 'my-app', version: '1.0' },
});
client.sendInitialized();

// Start thread
const { thread } = await client.threadStart({ cwd: '/my/project' });

// Register notification handlers
client.onNotification('item/agentMessage/delta', (params) => {
  process.stdout.write(params.delta);
});

client.onNotification('turn/completed', (params) => {
  console.log('\nTurn finished:', params.turn.status);
});

// Register approval handlers
client.onServerRequest(
  'item/commandExecution/requestApproval',
  async (params) => {
    return { decision: 'accept' };
  },
);

client.onServerRequest(
  'item/fileChange/requestApproval',
  async (params) => {
    return { decision: 'acceptForSession' };
  },
);

// Start turn
const { turn } = await client.turnStart({
  threadId: thread.id,
  input: [{ type: 'text', text: 'Fix the failing tests' }],
});
```

**Use cases:** Building custom Codex frontends, integrating into existing applications, test harnesses that need fine-grained control.

#### DO

- Keep every protocol method represented as a typed API with schema-derived params/results.
- Centralize request ID allocation, pending request tracking, and handler dispatch here.
- Use middleware only for cross-cutting mechanics that apply across methods.
- Treat server requests and notifications as first-class typed events.

#### DON'T

- Don't collapse multiple protocol steps into high-level convenience workflows.
- Don't let middleware mutate message semantics in ways the caller cannot reason about.
- Don't leak raw transport details into the public typed API.
- Don't duplicate stateful thread/turn modeling that belongs in Session Runtime.

#### Test Requirements

- Verify every generated client request method sends the expected method name and params.
- Verify responses resolve the matching pending promise by request ID, including out-of-order responses.
- Verify server request handlers return correctly typed responses and notification handlers fire exactly once.
- Verify middleware ordering is deterministic for incoming and outgoing messages.
- Verify timeouts, unknown methods, and transport failures reject pending work cleanly.

### Session Runtime

Formerly "Layer 2". This tier owns ergonomic workflow objects and long-lived client state such as sessions, threads, turns, and approval policy integration.

High-level object model with `Session`, `Thread`, `Turn`. Turns are `AsyncIterable<TurnEvent>` for streaming consumption. Approvals handled via injected `ApprovalPolicy`.

#### `ApprovalPolicy`

```ts
interface ApprovalPolicy {
  onCommandExecution?(
    params: CommandExecutionRequestApprovalParams,
  ): Promise<CommandExecutionApprovalDecision>;

  onFileChange?(
    params: FileChangeRequestApprovalParams,
  ): Promise<FileChangeApprovalDecision>;

  onToolRequestUserInput?(
    params: ToolRequestUserInputParams,
  ): Promise<ToolRequestUserInputResponse>;

  onDynamicToolCall?(
    params: DynamicToolCallParams,
  ): Promise<DynamicToolCallResponse>;
}

// Built-in policies
namespace ApprovalPolicy {
  /** Accept everything automatically */
  function autoAccept(): ApprovalPolicy;

  /** Decline everything automatically */
  function autoDecline(): ApprovalPolicy;

  /** Accept commands, decline file changes */
  function commandsOnly(): ApprovalPolicy;

  /** Custom rules via predicate functions */
  function custom(rules: {
    command?: (params: CommandExecutionRequestApprovalParams) => Promise<CommandExecutionApprovalDecision>;
    fileChange?: (params: FileChangeRequestApprovalParams) => Promise<FileChangeApprovalDecision>;
  }): ApprovalPolicy;
}
```

#### `Session`

```ts
class Session {
  /** Create a session, initialize the connection */
  static async create(options: {
    transport?: 'stdio' | 'websocket';
    command?: string;       // default: 'codex'
    args?: string[];        // default: ['app-server']
    wsUrl?: string;         // for websocket transport
    clientInfo: { name: string; version: string; title?: string };
    capabilities?: { experimentalApi?: boolean; optOutNotificationMethods?: string[] };
    approvalPolicy?: ApprovalPolicy;
    middleware?: Middleware[];
  }): Promise<Session>;

  /** The underlying TypedCodexClient (Typed Protocol Client escape hatch) */
  get client(): TypedCodexClient;

  /** Start a new thread */
  startThread(params?: Partial<ThreadStartParams>): Promise<Thread>;

  /** Resume an existing thread */
  resumeThread(threadId: string, params?: Partial<ThreadResumeParams>): Promise<Thread>;

  /** Fork an existing thread */
  forkThread(threadId: string): Promise<Thread>;

  /** List threads */
  listThreads(params?: ThreadListParams): Promise<{ threads: ThreadSummary[]; nextCursor: string | null }>;

  /** Read a thread (without resuming) */
  readThread(threadId: string, includeTurns?: boolean): Promise<ThreadData>;

  /** List available models */
  listModels(params?: ModelListParams): Promise<Model[]>;

  /** Execute a command without a thread */
  exec(command: string[], options?: { cwd?: string; sandboxPolicy?: SandboxPolicy; timeoutMs?: number }): Promise<ExecResult>;

  /** Register a global event listener (for notifications not tied to a specific thread) */
  on(event: string, handler: (...args: any[]) => void): this;

  /** Close the session and underlying connection */
  close(): Promise<void>;
}
```

#### `Thread`

```ts
class Thread {
  /** Thread ID */
  readonly id: string;

  /** Thread name (may be null until set) */
  readonly name: string | null;

  /** Start a new turn with text input */
  startTurn(input: string | UserInput[], options?: Partial<TurnStartParams>): Promise<Turn>;

  /** Shorthand: start a turn and wait for the final agent message text */
  ask(input: string | UserInput[], options?: Partial<TurnStartParams>): Promise<string>;

  /** Steer the active turn */
  steer(input: string | UserInput[], expectedTurnId: string): Promise<void>;

  /** Interrupt the active turn */
  interrupt(turnId: string): Promise<void>;

  /** Start a review */
  review(target: ReviewTarget, delivery?: 'inline' | 'detached'): Promise<Turn>;

  /** Archive this thread */
  archive(): Promise<void>;

  /** Unarchive this thread */
  unarchive(): Promise<Thread>;

  /** Fork this thread into a new one */
  fork(): Promise<Thread>;

  /** Rollback last N turns */
  rollback(numTurns: number): Promise<void>;

  /** Trigger compaction */
  compact(): Promise<void>;

  /** Unsubscribe from this thread */
  unsubscribe(): Promise<void>;

  /** Set thread name */
  setName(name: string): Promise<void>;

  /** Register per-thread event listener */
  on(event: string, handler: (...args: any[]) => void): this;
}
```

#### `Turn`

```ts
class Turn implements AsyncIterable<TurnEvent> {
  /** Turn ID */
  readonly id: string;

  /** Current status (updates as events arrive) */
  readonly status: 'inProgress' | 'completed' | 'interrupted' | 'failed';

  /** Accumulated items (populated as events stream in) */
  readonly items: ThreadItem[];

  /** Error details if status is 'failed' */
  readonly error: TurnError | null;

  /** Async iterate over turn events as they stream in */
  [Symbol.asyncIterator](): AsyncIterator<TurnEvent>;

  /** Wait for the turn to complete and return the final turn state */
  waitForCompletion(): Promise<CompletedTurn>;

  /** Get the final agent message text (waits for completion) */
  text(): Promise<string>;
}
```

#### `TurnEvent`

```ts
type TurnEvent =
  | { type: 'itemStarted'; item: ThreadItem }
  | { type: 'itemCompleted'; item: ThreadItem }
  | { type: 'agentMessageDelta'; itemId: string; delta: string }
  | { type: 'planDelta'; itemId: string; delta: string }
  | { type: 'reasoningDelta'; itemId: string; delta: string }
  | { type: 'reasoningSummaryDelta'; itemId: string; delta: string; summaryIndex: number }
  | { type: 'commandOutputDelta'; itemId: string; delta: string }
  | { type: 'fileChangeDelta'; itemId: string; delta: string }
  | { type: 'turnDiffUpdated'; diff: string }
  | { type: 'planUpdated'; explanation?: string; plan: PlanStep[] }
  | { type: 'error'; error: TurnError }
  | { type: 'completed'; turn: CompletedTurn };
```

#### Usage

**Simple: ask and get an answer**

```ts
import { Session, ApprovalPolicy } from 'codex-client';

const session = await Session.create({
  clientInfo: { name: 'my-app', version: '1.0' },
  approvalPolicy: ApprovalPolicy.autoAccept(),
});

const thread = await session.startThread({ cwd: '/my/project' });
const answer = await thread.ask('What does this project do?');
console.log(answer);

await session.close();
```

**Streaming: process events as they arrive**

```ts
const thread = await session.startThread({ cwd: '/my/project' });
const turn = await thread.startTurn('Fix all failing tests');

for await (const event of turn) {
  switch (event.type) {
    case 'agentMessageDelta':
      process.stdout.write(event.delta);
      break;
    case 'itemStarted':
      if (event.item.type === 'commandExecution') {
        console.log(`\n> Running: ${event.item.command}`);
      }
      break;
    case 'commandOutputDelta':
      process.stdout.write(event.delta);
      break;
    case 'itemCompleted':
      if (event.item.type === 'fileChange') {
        console.log(`\n  Changed: ${event.item.changes.map(c => c.path).join(', ')}`);
      }
      break;
    case 'completed':
      console.log(`\nDone: ${event.turn.status}`);
      break;
  }
}

console.log('All items:', turn.items);
```

**Custom approval policy**

```ts
const session = await Session.create({
  clientInfo: { name: 'secure-harness', version: '1.0' },
  approvalPolicy: ApprovalPolicy.custom({
    async command(params) {
      // Only allow non-destructive commands
      const cmd = params.command ?? '';
      if (/rm\s|sudo\s|chmod\s/.test(cmd)) {
        return { decision: 'decline' };
      }
      return { decision: 'accept' };
    },
    async fileChange(params) {
      return { decision: 'acceptForSession' };
    },
  }),
});
```

**Escaping to Typed Protocol Client for advanced use**

```ts
const session = await Session.create({ /* ... */ });

// Access the typed client directly
session.client.onNotification('account/rateLimits/updated', (params) => {
  console.log('Rate limits changed:', params.rateLimits);
});

// Use middleware
session.client.use(recordingMiddleware('./recordings'));
```

#### DO

- Model the user-facing lifecycle in domain terms: session, thread, turn, review, approval policy.
- Convert protocol notifications into stable, composable runtime events.
- Keep escape hatches available when advanced callers need lower-level control.
- Make the default path easy for common workflows like `ask`, streaming, and review.

#### DON'T

- Don't hide the underlying protocol so completely that debugging becomes impossible.
- Don't invent convenience methods that skip protocol guarantees or lifecycle constraints.
- Don't couple runtime objects to a single transport implementation.
- Don't mix test-only helpers into the production runtime surface.

#### Test Requirements

- Verify `Session.create()` performs initialization correctly and closes cleanly.
- Verify thread lifecycle methods call the expected typed client operations and update runtime state.
- Verify turn streaming preserves event order and final completion semantics.
- Verify approval policy hooks are invoked for the right server requests and their decisions are forwarded correctly.
- Verify `ask()`, `text()`, and other convenience APIs match the underlying streamed turn result.

### Type Generation

Types are auto-generated from the 157 JSON schema files in `schema/`:

```
scripts/generate-types.ts
  ├── Reads schema/*.json, schema/v1/*.json, schema/v2/*.json
  ├── Resolves $ref references between schema files
  ├── Converts JSON Schema → TypeScript interfaces/types
  ├── Generates discriminated unions for oneOf schemas (ThreadItem, UserInput, etc.)
  ├── Generates method-to-params/result type maps for client requests, server requests, notifications
  └── Outputs to src/types/generated/
```

Key generated type maps:

```ts
// Maps method string → params type for client requests
type ClientRequestMap = {
  'initialize': { params: InitializeParams; result: InitializeResponse };
  'thread/start': { params: ThreadStartParams; result: ThreadStartResponse };
  'turn/start': { params: TurnStartParams; result: TurnStartResponse };
  // ... all 40+ methods
};

// Maps method string → params type for server requests
type ServerRequestMap = {
  'item/commandExecution/requestApproval': {
    params: CommandExecutionRequestApprovalParams;
    result: CommandExecutionRequestApprovalResponse;
  };
  // ... all 6-8 server request methods
};

// Maps method string → params type for server notifications
type ServerNotificationMap = {
  'thread/started': ThreadStartedNotification;
  'turn/completed': TurnCompletedNotification;
  'item/agentMessage/delta': AgentMessageDeltaNotification;
  // ... all 30+ notification methods
};
```

### Transport Abstraction

```ts
// StdioTransport spawns `codex app-server` as a child process
class StdioTransport implements Transport {
  constructor(options: {
    command?: string;   // default: 'codex'
    args?: string[];    // default: ['app-server']
    env?: Record<string, string>;
    cwd?: string;
  });
}

// WebSocketTransport connects to a running app-server
class WebSocketTransport implements Transport {
  constructor(url: string);  // e.g. 'ws://127.0.0.1:4500'
}
```

### Middleware System

Middleware intercepts messages in Typed Protocol Client before they reach handlers. Inspired by Koa/Express middleware pattern.

```ts
interface MiddlewareContext {
  /** The raw JSON-RPC message */
  message: JsonRpcMessage;

  /** Direction: 'outgoing' (client→server) or 'incoming' (server→client) */
  direction: 'outgoing' | 'incoming';

  /** Parsed method name (if present) */
  method?: string;

  /** Timestamp */
  timestamp: number;
}

type Middleware = (ctx: MiddlewareContext, next: () => Promise<void>) => Promise<void>;
```

#### Built-in Middleware

**Logging:**
```ts
function loggingMiddleware(options?: {
  level?: 'debug' | 'info';
  filter?: (ctx: MiddlewareContext) => boolean;
  logger?: (msg: string) => void;
}): Middleware;
```

**Recording (for test fixture generation):**
```ts
function recordingMiddleware(options: {
  outputPath: string;         // directory to write recordings
  sessionName?: string;       // recording file name
}): Middleware & {
  /** Flush buffered messages and finalize the recording */
  finalize(): Promise<string>;  // returns recording file path
};
```

**Auto-Approval:**
```ts
function autoApprovalMiddleware(options?: {
  commands?: 'accept' | 'acceptForSession' | 'decline';
  fileChanges?: 'accept' | 'acceptForSession' | 'decline';
}): Middleware;
```

### Testing Infrastructure

The testing stack should enforce the contract at each tier, not just happy-path examples.

#### `MockTransport`

In-memory transport for unit tests. Allows programmatic injection of server messages.

```ts
class MockTransport implements Transport {
  /** Inject a server message (as if the server sent it) */
  injectServerMessage(msg: JsonRpcMessage): void;

  /** Get all messages sent by the client */
  readonly sentMessages: JsonRpcMessage[];

  /** Wait for the client to send a message matching a predicate */
  waitForSent(predicate: (msg: JsonRpcMessage) => boolean, timeoutMs?: number): Promise<JsonRpcMessage>;
}
```

#### `ReplayTransport`

Replays a recorded protocol session. Validates that client messages match expectations.

```ts
class ReplayTransport implements Transport {
  constructor(recordingPath: string, options?: {
    /** How strictly to match outgoing messages */
    matchMode?: 'exact' | 'method-only' | 'relaxed';
    /** Timing: replay at recorded pace or as fast as possible */
    timing?: 'realtime' | 'instant';
  });
}
```

#### `fixtures`

Factory functions for building protocol messages in tests:

```ts
namespace fixtures {
  function initializeResponse(userAgent?: string): JsonRpcResponse;
  function threadStartResponse(threadId?: string): JsonRpcResponse;
  function turnStartResponse(turnId?: string): JsonRpcResponse;
  function itemStarted(item: Partial<ThreadItem>): JsonRpcNotification;
  function itemCompleted(item: Partial<ThreadItem>): JsonRpcNotification;
  function agentMessageDelta(itemId: string, delta: string): JsonRpcNotification;
  function turnCompleted(turnId: string, status?: string): JsonRpcNotification;
  function commandApprovalRequest(id: number, params: Partial<CommandExecutionRequestApprovalParams>): JsonRpcRequest;
  // ... etc
}
```

#### Testing Example

```ts
import { TypedCodexClient, MockTransport, fixtures } from 'codex-client';

test('handles a simple turn', async () => {
  const transport = new MockTransport();
  const client = new TypedCodexClient(transport);

  // Simulate server responses
  const initPromise = client.initialize({
    clientInfo: { name: 'test', version: '0.1' },
  });
  transport.injectServerMessage(fixtures.initializeResponse());
  await initPromise;

  const threadPromise = client.threadStart({ cwd: '/tmp' });
  transport.injectServerMessage(fixtures.threadStartResponse('thr_1'));
  const { thread } = await threadPromise;

  expect(thread.id).toBe('thr_1');

  // Register handler & simulate delta stream
  const deltas: string[] = [];
  client.onNotification('item/agentMessage/delta', (p) => deltas.push(p.delta));

  transport.injectServerMessage(fixtures.agentMessageDelta('item_1', 'Hello'));
  transport.injectServerMessage(fixtures.agentMessageDelta('item_1', ' world'));

  expect(deltas).toEqual(['Hello', ' world']);
});
```

#### Cross-Tier Test Requirements

- Protocol Core must be covered primarily by small deterministic unit tests.
- Typed Protocol Client must have dispatch and middleware tests that run entirely against `MockTransport`.
- Session Runtime must have lifecycle tests that assert observable behavior rather than internal implementation details.
- Replay fixtures must be versioned and used to lock down real protocol traces for regression coverage.
- At least one end-to-end integration test must exercise a real `codex app-server` flow before release.

---

## Implementation Plan

Ordered bottom-up, each phase produces a usable, shippable artifact.

### Phase 1: Foundation

1. **Project setup** — `package.json`, `tsconfig.json`, build tooling, linting
2. **Type generation** (`scripts/generate-types.ts`) — Parse all 157 JSON schemas, resolve `$ref`, generate TypeScript types, discriminated unions, and method maps
3. **Transport interface + StdioTransport** — Spawn `codex app-server` as child process, JSONL read/write

### Phase 2: Protocol Core

4. **JsonRpcCodec** — Parse/serialize JSON-RPC messages (handle omitted `jsonrpc` field)
5. **ProtocolConnection** — Bidirectional async iterable message pump over any `Transport`

### Phase 3: Typed Protocol Client

6. **IdGenerator** — Auto-incrementing request ID allocation
7. **RequestRouter** — Match incoming messages to pending requests and registered handlers
8. **TypedCodexClient** — Typed methods for all client requests, `onServerRequest()`, `onNotification()`
9. **Middleware system** — `use()`, middleware runner, context object

### Phase 4: Built-in Middleware

10. **loggingMiddleware** — Configurable message logging
11. **recordingMiddleware** — Capture protocol sessions to disk
12. **autoApprovalMiddleware** — Configurable auto-approval for commands and file changes

### Phase 5: Session Runtime

13. **ApprovalPolicy** — Interface + `autoAccept()`, `autoDecline()`, `custom()`
14. **Session** — Create/close lifecycle, wraps `TypedCodexClient`
15. **Thread** — Thread methods, per-thread event routing
16. **Turn** — `AsyncIterable<TurnEvent>`, item accumulation, `waitForCompletion()`, `text()`

### Phase 6: Testing Infrastructure

17. **MockTransport** — In-memory transport with message injection
18. **ReplayTransport** — Replay recorded sessions
19. **fixtures** — Factory functions for protocol messages

### Phase 7: Polish

20. **WebSocketTransport** — WebSocket transport implementation
21. **Error handling** — Typed errors, timeout handling, reconnection
22. **Documentation** — API docs, usage examples
23. **Integration tests** — End-to-end tests against a real `codex app-server`
