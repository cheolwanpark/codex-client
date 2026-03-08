# codex-harness-kit

Async Python protocol-core bindings for the Codex app-server protocol.

## Development

```bash
uv sync --dev
uv run pytest -m "not integration"
uv run pytest -m integration
```
