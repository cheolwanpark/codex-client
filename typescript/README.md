# codex-client for TypeScript

TypeScript bindings for the Codex app-server protocol.

This package currently implements only the protocol core layer:

- `JsonRpcCodec`
- `ProtocolConnection`
- `StdioTransport`
- JSON-RPC message and error types

Higher layers such as a typed protocol client and session runtime will be added later.

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
import { ProtocolConnection, StdioTransport } from "@codex-client/typescript";

const transport = new StdioTransport();
const connection = new ProtocolConnection(transport);

await connection.send({
  id: 1,
  method: "initialize",
  params: {
    clientInfo: {
      name: "my-app",
      version: "0.1.0",
    },
  },
});
```
