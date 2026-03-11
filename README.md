# codex-client

Repo-first SDK work for the Codex app-server protocol.

This repository contains Python and TypeScript bindings for the Codex app-server protocol, plus the schemas and design notes that define the shared wire model. The goal is to make it practical to embed Codex in a host application without rebuilding the JSON-RPC transport, typed method surface, and runtime orchestration yourself.

## What Is Codex App-Server?

`codex app-server` runs Codex as a local bidirectional JSON-RPC service. A host connects to it, performs `initialize`, sends `initialized`, starts or resumes threads, starts turns, and then consumes streaming notifications and server-originated requests for output, plans, approvals, tool input, and completion.

This repository is organized around that protocol:

- `schema/` defines the wire format
- `DESIGN.md` defines the shared lifecycle and layering rules
- `python/` is the behavioral reference binding
- `typescript/` implements the same three-layer model in TypeScript

## High-Level Architecture

```text
Your App
  |
  v
codex-client/python or codex-client/typescript
  |
  +-- Session Runtime
  |     Session -> Thread -> Turn
  |     ApprovalPolicy hooks
  |
  +-- Typed Protocol Client
  |     TypedCodexClient
  |     Generated request/response wrappers
  |
  +-- Protocol Core
  |     StdioTransport
  |     ProtocolConnection
  |     JsonRpcCodec
  |
  v
codex app-server
  |
  v
Codex
```

Supporting artifacts in this repo:

- `schema/` is the source of truth for the app-server API surface
- `python/scripts/generate_protocol_client.py` and `typescript/scripts/generate-protocol-client.mjs` generate checked-in typed protocol surfaces
- `DESIGN.md` is the shared cross-language design reference

## Repository Layout

- `python/` contains the Python package, examples, tests, and generation script
- `typescript/` contains the TypeScript package, examples, tests, and generation script
- `schema/` contains the Codex app-server JSON schemas used by both bindings
- `DESIGN.md` documents the shared protocol lifecycle, object model, and SDK layering

## README Map

- [`python/README.md`](python/README.md): full Python SDK guide, examples, and development commands
- [`python/examples/README.md`](python/examples/README.md): Python example progression
- [`typescript/README.md`](typescript/README.md): full TypeScript SDK guide, examples, and development commands
- [`typescript/examples/README.md`](typescript/examples/README.md): TypeScript example progression
- [`DESIGN.md`](DESIGN.md): cross-language protocol and architecture reference

## Support Level

- Python is the behavioral reference binding in this repository
- TypeScript now implements all three layers: protocol core, typed client, and session runtime
- both bindings include live `codex app-server` integration smoke tests

## Getting Started

If you want to use the SDK directly:

- start with [`python/README.md`](python/README.md) for the Python binding
- start with [`typescript/README.md`](typescript/README.md) for the TypeScript binding

If you want the shared protocol and architecture rules first, read [`DESIGN.md`](DESIGN.md).
