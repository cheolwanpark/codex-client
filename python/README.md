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

## Development

```bash
uv sync --dev
uv run python scripts/generate_protocol_client.py
uv run pytest -m "not integration"
uv run pytest -m integration
```
