# codex-client

Repo-first SDK work for the Codex app-server protocol.

This repository currently contains a Python binding and an early TypeScript binding for the Codex app-server protocol, plus the JSON schemas and design notes that define the protocol surface. The goal is to make it practical to embed Codex in your own host application without starting from raw JSON-RPC messages.

## What Is Codex App-Server?

`codex app-server` runs Codex as a local bidirectional JSON-RPC service. A host application connects to it, performs `initialize`, starts or resumes threads, starts turns, and then consumes streaming notifications for agent output, plans, tool calls, approvals, and completion.

That app-server layer is the feature this repository is built around:

- the protocol schemas in `schema/` describe the wire format
- the Python package wraps the protocol at several abstraction levels
- the TypeScript package currently implements the protocol core layer
- the examples and tests exercise real `codex app-server` flows

## High-Level Architecture

```text
Your App
  |
  v
codex-client/python
  |
  +-- Session Runtime
  |     Session -> Thread -> Turn
  |     ApprovalPolicy hooks
  |
  +-- Typed Protocol Client
  |     TypedCodexClient
  |     Generated request/response methods
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

- `schema/` is the source of truth for the app-server API surface.
- `python/scripts/generate_protocol_client.py` turns schema data into generated Python protocol types and client helpers.
- `DESIGN.md` is the shared cross-language design reference for protocol semantics and SDK layering.

## Repository Layout

- `python/` contains the Python package, examples, tests, and generation script.
- `typescript/` contains the TypeScript package for the protocol core layer.
- `schema/` contains the Codex app-server JSON schemas used to drive typed bindings.
- `DESIGN.md` documents the shared protocol lifecycle, object model, and multi-language SDK architecture.
- `claude-agent-toolkit/` is a separate sibling project used here as a documentation/style reference, not part of the Python package itself.

## README Map

- [`python/README.md`](python/README.md): primary SDK documentation, setup, quickstarts, examples, and development commands
- [`typescript/README.md`](typescript/README.md): TypeScript protocol-core setup, API surface, and test commands

Python is currently the most complete binding in this repository. The TypeScript binding currently covers the protocol core only.

## Getting Started

If you want to use the SDK, start with [`python/README.md`](python/README.md).

If you want the cross-language protocol and architecture reference first, read [`DESIGN.md`](DESIGN.md).
