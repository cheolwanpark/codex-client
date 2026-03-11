# codex-client for TypeScript

Async TypeScript bindings for the Codex app-server protocol, from raw JSON-RPC transport up to `Session` / `Thread` / `Turn` runtime helpers.

## What You Get

- **Protocol Core**: `JsonRpcCodec`, `ProtocolConnection`, and `StdioTransport`
- **Typed Protocol Client**: `TypedCodexClient` with generated request methods, notification routing, and server-request handlers
- **Session Runtime**: `Session`, `Thread`, `Turn`, and `ApprovalPolicy`
- **Generated Protocol Types**: request, response, notification, and server-request types derived from `schema/`
- **Usability Helpers**: `clientInfo(...)`, `threadParams(...)`, `turnOptions(...)`, `textInput(...)`, and approval-response helpers
- **Examples and Integration Tests**: repo-local examples plus live `codex app-server` smoke tests for all three layers

## Prerequisites

- Node.js 20+
- `pnpm`
- `codex` CLI installed and available on `PATH`
- an authenticated local Codex CLI session for live integration tests and examples

## Setup

From the repo root:

```bash
cd typescript
pnpm install
```

## Quick Start

```ts
import { Session, clientInfo } from "@codex-client/typescript";

const session = await Session.create({
  clientInfo: clientInfo("my-app", "0.1.0"),
});

try {
  const thread = await session.startEphemeralThread();
  const answer = await thread.ask("Reply with exactly OK.");
  console.log(answer.trim());
} finally {
  await session.close();
}
```

## Choose Your Layer

### Session Runtime

Use this for the common host flow:

- `Session.create(...)`
- `session.startEphemeralThread(...)`, `session.startThread(...)`, `session.resumeThread(...)`
- `thread.ask(...)` or `thread.startTurn(...)`
- `ApprovalPolicy` hooks for approvals and tool participation

Streaming stays visible through `Turn`, which is a single-consumer `AsyncIterable<TurnEvent>`.

### Typed Protocol Client

Use this when you want typed requests and notifications without the runtime wrapper:

- generated methods such as `threadStart(...)` and `turnStart(...)`
- `onNotification(...)`
- `waitForNotification(...)`
- `onServerRequest(...)`

```ts
import {
  StdioTransport,
  TypedCodexClient,
  clientInfo,
  textInput,
} from "@codex-client/typescript";

const client = TypedCodexClient.fromTransport(new StdioTransport());
const chunks: string[] = [];

client.onNotification("item/agentMessage/delta", (params) => {
  chunks.push(params.delta);
});

try {
  await client.initialize({ clientInfo: clientInfo("my-app", "0.1.0") });
  await client.sendInitialized();

  const thread = await client.threadStart({ ephemeral: true });
  await client.turnStart({
    input: [textInput("Reply with exactly OK.")],
    threadId: thread.thread.id,
  });

  const completed = await client.waitForNotification("turn/completed", {
    timeoutMs: 60_000,
  });
  console.log(completed.turn.status);
  console.log(chunks.join("").trim());
} finally {
  await client.close();
}
```

### Protocol Core

Use this when you need direct transport and JSON-RPC message control:

- `StdioTransport`
- `ProtocolConnection`
- `JsonRpcCodec`

This layer is intentionally minimal and is the base for the typed client.

## Examples

Runnable source examples live in [`examples/README.md`](examples/README.md).

Recommended order:

- `01_quickstart.ts`
- `02_streaming_turn.ts`
- `03_resume_thread.ts`
- `04_approval_policy.ts`
- `05_low_level_client.ts`

Run them from `typescript/` with:

```bash
pnpm example:quickstart
pnpm example:streaming
pnpm example:resume
pnpm example:approval
pnpm example:low-level
```

## Code Generation

The checked-in schema files in `../schema/` are the source of truth for protocol shapes.

When protocol-facing TypeScript definitions change:

```bash
cd typescript
pnpm generate
```

This regenerates:

- `src/generated.ts`
- `src/generated-client.ts`

Do not hand-edit generated protocol surfaces. Update schema/codegen inputs and regenerate.

## Development

From `typescript/`:

```bash
pnpm generate
pnpm examples:build
pnpm test
pnpm typecheck
pnpm build
```

Test notes:

- `pnpm test` includes unit tests plus live integration smoke tests when `codex` is available locally
- integration coverage now exercises the protocol core, typed client, and runtime layers
- `pnpm typecheck` includes `src/`, `tests/`, and `examples/`

## Contributing Notes

- `schema/` is authoritative for wire shapes
- `DESIGN.md` is authoritative for lifecycle and layering invariants
- keep TypeScript behavior aligned with the Python binding where parity matters
- preserve the three-layer separation: protocol core -> typed client -> runtime
- keep Node as the default runtime unless a task explicitly expands runtime support
