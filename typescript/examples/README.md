# TypeScript Examples

These examples are organized by abstraction level. Start at the runtime layer, then drop to the typed client only when you need more control over request and notification flow.

## Prerequisites

- `pnpm install`
- `codex` CLI installed and available on `PATH`
- an authenticated local Codex CLI session

Run examples from the `typescript/` directory:

```bash
pnpm example:quickstart
pnpm example:streaming
pnpm example:resume
pnpm example:approval
pnpm example:low-level
```

These commands build the examples and the local `src/` tree into `.examples-dist/`, then run the compiled example with Node.

## Progression

### `01_quickstart.ts`

The shortest runtime path:

- create a `Session`
- start an ephemeral thread
- use `thread.ask(...)`

### `02_streaming_turn.ts`

The runtime streaming model:

- start a turn explicitly
- iterate over `Turn` events
- print agent deltas as they arrive

### `03_resume_thread.ts`

Reconnect to a persistent thread:

- start a non-ephemeral thread
- close the first session
- `resumeThread(...)` from a fresh session

### `04_approval_policy.ts`

Host-controlled approvals:

- build `ApprovalPolicy.custom(...)`
- return typed helper payloads for approvals and tool input
- attach the policy to a real session

### `05_low_level_client.ts`

Typed protocol access without the runtime wrapper:

- use `TypedCodexClient.fromTransport(...)`
- call `initialize(...)` and `sendInitialized()`
- register notification handlers
- start threads and turns with generated methods
- wait for completion with `waitForNotification(...)`
