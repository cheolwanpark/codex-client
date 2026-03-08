# codex-harness-kit

Async Python bindings for the Codex app-server protocol.

Current layers:

- Protocol Core: `JsonRpcCodec`, `ProtocolConnection`, `StdioTransport`
- Typed Protocol Client: `TypedCodexClient`

## Development

```bash
uv sync --dev
uv run python scripts/generate_protocol_client.py
uv run pytest -m "not integration"
uv run pytest -m integration
```
