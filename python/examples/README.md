# Python Examples

These examples are organized by abstraction level. Start at the runtime layer, then move down only if you need more control. The examples prefer the public helper functions, enums, and typed protocol imports over handwritten dicts and string literals.

## Prerequisites

- `uv sync --dev`
- `codex` CLI installed and available on `PATH`
- authenticated local Codex CLI session

Run examples from the `python/` directory:

```bash
uv run python examples/01_quickstart.py
uv run python examples/02_streaming_turn.py
uv run python examples/03_resume_thread.py
uv run python examples/04_multi_session.py
uv run python examples/05_approval_policy.py
uv run python examples/06_low_level_client.py
```

## Progression

### `01_quickstart.py`

The default path for most users.

- create a `Session`
- use `start_ephemeral_thread()` for the common case
- send one prompt with `thread.ask(...)`

### `02_streaming_turn.py`

The runtime streaming model.

- start a turn explicitly
- iterate over `Turn` events with `TurnEventType`
- inspect deltas, plan updates, and completion

### `03_resume_thread.py`

Reconnect to a persistent thread from a fresh host session.

- start a non-ephemeral thread with `thread_params(ephemeral=False)`
- close the first session
- `resume_thread(...)` from a new session
- continue the conversation on the same thread

### `04_multi_session.py`

Run multiple independent host sessions at the same time.

- create separate `Session` instances concurrently
- show that each gets its own thread and answer
- contrast independent sessions with the `resume_thread(...)` flow

### `05_approval_policy.py`

Host-controlled approvals.

- build an `ApprovalPolicy.custom(...)`
- use typed hook params from `codex_harness_kit.protocol_types`
- use approval helper functions for common responses
- attach the policy to a real session

### `06_low_level_client.py`

Typed protocol access without the runtime wrapper.

- use `TypedCodexClient.from_transport(...)`
- call `initialize(...)` and `send_initialized()`
- register notification handlers with `NotificationMethod`
- await completion with `wait_for_notification(...)`
- start threads and turns with typed client methods
