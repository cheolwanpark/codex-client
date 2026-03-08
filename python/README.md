# codex-harness-kit

Async Python bindings for the Codex app-server protocol.

Current layers:

- Protocol Core: `JsonRpcCodec`, `ProtocolConnection`, `StdioTransport`
- Typed Protocol Client: `TypedCodexClient`
- Session Runtime: `Session`, `Thread`, `Turn`, `ApprovalPolicy`

## Quickstart

```python
from codex_harness_kit import ApprovalPolicy, Session


async with await Session.create(
    client_info={"name": "my-app", "version": "0.1.0"},
    approval_policy=ApprovalPolicy.auto_accept(),
) as session:
    thread = await session.start_thread({"ephemeral": True})
    answer = await thread.ask("Reply with exactly OK.")
    print(answer)
```

```python
from codex_harness_kit import ApprovalPolicy, Session


async with await Session.create(
    client_info={"name": "my-app", "version": "0.1.0"},
    approval_policy=ApprovalPolicy.auto_accept(),
) as session:
    thread = await session.start_thread({"ephemeral": True})
    turn = await thread.start_turn("Explain this repository")

    async for event in turn:
        if event["type"] == "agent_message_delta":
            print(event["delta"], end="")
```

## Examples

Runnable examples live in [`examples/README.md`](examples/README.md).

Recommended order:

- `01_quickstart.py`
- `02_streaming_turn.py`
- `03_resume_thread.py`
- `04_multi_session.py`
- `05_approval_policy.py`
- `06_low_level_client.py`

From the `python/` directory:

```bash
uv run python examples/01_quickstart.py
```

## Development

```bash
uv sync --dev
uv run python scripts/generate_protocol_client.py
uv run pytest -m "not integration"
uv run pytest -m integration
```
