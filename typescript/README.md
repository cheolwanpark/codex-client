# codex-client for TypeScript

TypeScript bindings for the Codex app-server protocol.

This package currently implements:

- `JsonRpcCodec`
- `ProtocolConnection`
- `StdioTransport`
- JSON-RPC message and error types
- generated protocol types and method registries
- `TypedCodexClient`

The higher-level session runtime is not implemented yet.

## Development

From the repository root:

```bash
cd typescript
pnpm install
pnpm test
pnpm typecheck
pnpm build
```

## Example

```ts
import { StdioTransport, TypedCodexClient } from "@codex-client/typescript";

const client = TypedCodexClient.fromTransport(new StdioTransport());

await client.initialize(
  {
    clientInfo: {
      name: "my-app",
      version: "0.1.0",
    },
  },
  { timeoutMs: 5_000 },
);
await client.sendInitialized();
```
