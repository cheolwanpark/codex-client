# codex-client for TypeScript

TypeScript bindings for the Codex app-server protocol.

This package currently implements:

- `JsonRpcCodec`
- `ProtocolConnection`
- `StdioTransport`
- JSON-RPC message and error types
- generated protocol types and method registries
- `TypedCodexClient`
- `ApprovalPolicy`
- `Session`
- `Thread`
- `Turn`
- helper builders for common runtime payloads

## Development

From the repository root:

```bash
cd typescript
pnpm install
pnpm test
pnpm typecheck
pnpm build
```

## Layers

- protocol core: `JsonRpcCodec`, `ProtocolConnection`, `StdioTransport`
- typed protocol client: `TypedCodexClient`
- session runtime: `Session`, `Thread`, `Turn`, `ApprovalPolicy`

## Runtime Example

```ts
import { Session, clientInfo } from "@codex-client/typescript";

const session = await Session.create({
  clientInfo: clientInfo("my-app", "0.1.0"),
});

try {
  const thread = await session.startEphemeralThread();
  const answer = await thread.ask("Reply with exactly OK.");
  console.log(answer);
} finally {
  await session.close();
}
```

## Typed Client Example

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

## Examples

See `typescript/examples/` for:

- quickstart
- streaming turn output
- resume thread
- approval policy
