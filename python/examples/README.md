# Python Examples

These examples are organized by abstraction level. Start at the runtime layer, then move down only if you need more control.

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
- start an ephemeral thread
- send one prompt with `thread.ask(...)`

### `02_streaming_turn.py`

The runtime streaming model.

- start a turn explicitly
- iterate over `Turn` events
- inspect deltas, plan updates, and completion

### `03_resume_thread.py`

Reconnect to a persistent thread from a fresh host session.

- start a non-ephemeral thread
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
- inspect the return shape for each host hook
- attach the policy to a real session

### `06_low_level_client.py`

Typed protocol access without the runtime wrapper.

- use `TypedCodexClient.from_transport(...)`
- call `initialize(...)` and `send_initialized()`
- register notification handlers directly
- start threads and turns with typed client methods
