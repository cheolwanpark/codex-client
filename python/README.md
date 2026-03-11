# codex-client for Python

Async Python bindings for the Codex app-server protocol, from raw JSON-RPC transport up to `Session` / `Thread` / `Turn` runtime helpers.

## Table of Contents

- [Why codex-client?](#why-codex-client)
- [What You Get](#what-you-get)
- [Quick Start](#quick-start)
- [Installation and Setup](#installation-and-setup)
- [Usage Quickstarts](#usage-quickstarts)
- [Choose Your Layer](#choose-your-layer)
- [Architecture](#architecture)
- [Examples](#examples)
- [Development](#development)
- [Notes and Constraints](#notes-and-constraints)

## Why codex-client?

The Codex app-server protocol is powerful, but the raw interface is still a bidirectional JSON-RPC stream. A host needs to:

1. spawn or connect to `codex app-server`
2. send `initialize` and `initialized`
3. issue typed requests such as `thread/start` and `turn/start`
4. route streaming notifications for deltas, plans, approvals, and completion
5. respond to server requests for command approval, file approval, tool input, and dynamic tool calls

This package gives you progressively higher-level entry points so you can stop at the layer you actually need instead of rebuilding that stack every time.

## What You Get

- **Protocol Core**: `JsonRpcCodec`, `ProtocolConnection`, and `StdioTransport` for raw message transport.
- **Typed Protocol Client**: `TypedCodexClient` with generated methods for the Codex app-server request surface.
- **Session Runtime**: `Session`, `Thread`, `Turn`, and `ApprovalPolicy` for the common host workflow.
- **Generated Protocol Types**: request, response, notification, and item types derived from the checked-in schemas.
- **Usability Helpers**: `client_info(...)`, `thread_params(...)`, `turn_options(...)`, `text_input(...)`, and approval helper functions.
- **Public Constants**: `NotificationMethod`, `ServerRequestMethod`, and `TurnEventType` for the most common string-based APIs.
- **Host-Controlled Approvals**: accept, decline, or customize command/file/tool approval handling in Python.
- **Examples and Integration Tests**: runnable scripts and tests that exercise a real local `codex app-server`.

## Quick Start

```python
from __future__ import annotations

import asyncio

from codex_client import ApprovalPolicy, Session, client_info


async def main() -> None:
    async with await Session.create(
        client_info=client_info("my-app", "0.1.0"),
        approval_policy=ApprovalPolicy.auto_accept(),
    ) as session:
        thread = await session.start_ephemeral_thread()
        answer = await thread.ask("Reply with exactly OK.")
        print(answer.strip())


if __name__ == "__main__":
    asyncio.run(main())
```

## Installation and Setup

### Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/)
- `codex` CLI installed and available on `PATH`
- an authenticated local Codex CLI session

### Set Up From This Repository

From the repo root:

```bash
cd python
uv sync --dev
```

### Quick Verification

From `python/`:

```bash
uv run python examples/01_quickstart.py
```

If your local Codex CLI session is ready, the example should print `OK`.

## Usage Quickstarts

### Basic Ask Flow

Use the runtime layer when you want the shortest path from prompt to answer.

```python
from __future__ import annotations

import asyncio

from codex_client import ApprovalPolicy, Session, client_info


async def main() -> None:
    async with await Session.create(
        client_info=client_info("my-app", "0.1.0"),
        approval_policy=ApprovalPolicy.auto_accept(),
    ) as session:
        thread = await session.start_ephemeral_thread()
        answer = await thread.ask("Summarize this repository in one sentence.")
        print(answer.strip())


if __name__ == "__main__":
    asyncio.run(main())
```

### Stream Turn Events

Use `start_turn(...)` when you want incremental output, plan updates, or final turn state.

```python
from __future__ import annotations

import asyncio

from codex_client import ApprovalPolicy, Session, TurnEventType, client_info


async def main() -> None:
    async with await Session.create(
        client_info=client_info("my-app", "0.1.0"),
        approval_policy=ApprovalPolicy.auto_accept(),
    ) as session:
        thread = await session.start_ephemeral_thread()
        turn = await thread.start_turn("Explain this SDK in one paragraph.")

        async for event in turn:
            if event["type"] == TurnEventType.AGENT_MESSAGE_DELTA:
                print(event["delta"], end="", flush=True)
            elif event["type"] == TurnEventType.PLAN_UPDATED:
                print("\n[plan updated]")
                for step in event["plan"]:
                    print(step["status"], step["step"])
            elif event["type"] == TurnEventType.COMPLETED:
                print(f"\nstatus={event['turn']['status']}")


if __name__ == "__main__":
    asyncio.run(main())
```

### Resume A Persistent Thread Across Sessions

Persistent threads let one host process reconnect later.

```python
from __future__ import annotations

import asyncio

from codex_client import ApprovalPolicy, Session, client_info, thread_params


async def main() -> None:
    async with await Session.create(
        client_info=client_info("my-app", "0.1.0"),
        approval_policy=ApprovalPolicy.auto_accept(),
    ) as first_session:
        thread = await first_session.start_thread(thread_params(ephemeral=False))
        await thread.ask("Reply with exactly FIRST.")
        thread_id = thread.id

    async with await Session.create(
        client_info=client_info("my-app", "0.1.0"),
        approval_policy=ApprovalPolicy.auto_accept(),
    ) as second_session:
        thread = await second_session.resume_thread(thread_id)
        snapshot = await second_session.read_thread(thread.id, include_turns=True)
        print(len(snapshot.get("turns", [])))
        print((await thread.ask("Reply with exactly SECOND.")).strip())


if __name__ == "__main__":
    asyncio.run(main())
```

### Run Multiple Independent Sessions

Each `Session` owns its own app-server connection and thread lifecycle.

```python
import asyncio

from codex_client import ApprovalPolicy, Session, client_info


async def run_once(prompt: str) -> str:
    async with await Session.create(
        client_info=client_info("my-app", "0.1.0"),
        approval_policy=ApprovalPolicy.auto_accept(),
    ) as session:
        thread = await session.start_ephemeral_thread()
        return (await thread.ask(prompt)).strip()


async def main() -> None:
    answers = await asyncio.gather(
        run_once("Reply with exactly SESSION_A."),
        run_once("Reply with exactly SESSION_B."),
    )
    print(answers)


if __name__ == "__main__":
    asyncio.run(main())
```

### Customize Approval Policy

The runtime is fail-closed by default. If you do not provide an approval hook, the default behavior is to decline.

```python
from __future__ import annotations

import asyncio

from codex_client import ApprovalPolicy, Session, approve_command, client_info
from codex_client.protocol_types import (
    CommandExecutionRequestApprovalParams,
    CommandExecutionRequestApprovalResponse,
)


async def on_command_execution(
    params: CommandExecutionRequestApprovalParams,
) -> CommandExecutionRequestApprovalResponse:
    print(f"command approval requested for {params['itemId']}")
    return approve_command()


async def main() -> None:
    policy = ApprovalPolicy.custom(on_command_execution=on_command_execution)

    async with await Session.create(
        client_info=client_info("my-app", "0.1.0"),
        approval_policy=policy,
    ) as session:
        thread = await session.start_ephemeral_thread()
        print((await thread.ask("Reply with exactly OK.")).strip())


if __name__ == "__main__":
    asyncio.run(main())
```

Built-in policies:

- `ApprovalPolicy.auto_accept()`
- `ApprovalPolicy.auto_decline()`
- `ApprovalPolicy.commands_only()`
- `ApprovalPolicy.custom(...)`

Raw dict responses still work when you need full protocol control, but the helper functions keep the common approval shapes readable.

### Use The Low-Level Typed Client Directly

Drop to `TypedCodexClient` when you want direct request/notification control without the runtime wrapper.

```python
from __future__ import annotations

from codex_client import (
    NotificationMethod,
    StdioTransport,
    TypedCodexClient,
    client_info,
    text_input,
)


async def main() -> None:
    client = TypedCodexClient.from_transport(StdioTransport())
    chunks: list[str] = []

    client.on_notification(
        NotificationMethod.ITEM_AGENT_MESSAGE_DELTA,
        lambda params: chunks.append(params["delta"]),
    )

    try:
        await client.initialize({"clientInfo": client_info("my-app", "0.1.0")})
        await client.send_initialized()

        thread = await client.thread_start({"ephemeral": True})
        thread_id = thread["thread"]["id"]

        await client.turn_start(
            {
                "threadId": thread_id,
                "input": [text_input("Reply with exactly OK.")],
            }
        )

        result = await client.wait_for_notification(
            NotificationMethod.TURN_COMPLETED,
            timeout=60.0,
        )
        print(result["turn"]["status"])
        print("".join(chunks).strip())
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
```

## Choose Your Layer

### Session Runtime

Use this when you want an application-facing object model:

- `Session.create(...)`
- `session.start_ephemeral_thread(...)`, `session.start_thread(...)`, or `session.resume_thread(...)`
- `thread.ask(...)` or `thread.start_turn(...)`
- `ApprovalPolicy` hooks for approvals and user input

This is the default starting point for most hosts.

### Typed Protocol Client

Use this when you want typed method calls but still want to manage routing yourself:

- register notification handlers with `on_notification(...)`
- wait on a single notification with `wait_for_notification(...)`
- register server request handlers with `on_server_request(...)`
- call generated methods such as `thread_start(...)` and `turn_start(...)`

This is useful when you need custom orchestration but do not want to work at raw JSON-RPC message level.

### Protocol Core

Use this when you need direct transport and message control:

- `StdioTransport`
- `ProtocolConnection`
- `JsonRpcCodec`

This layer is intentionally minimal.

## Architecture

The Python package implements the same three-layer model described in `DESIGN.md`.

```text
Session / Thread / Turn / ApprovalPolicy
                |
                v
         TypedCodexClient
                |
                v
StdioTransport -> ProtocolConnection -> JsonRpcCodec
                |
                v
         codex app-server
```

Layer responsibilities:

- **Protocol Core** handles process I/O and JSON-RPC framing.
- **Typed Protocol Client** turns protocol methods into Python methods and routes responses, notifications, and server requests.
- **Session Runtime** keeps thread and turn state in sync and exposes a higher-level host API.

## Examples

Runnable examples live in [`examples/README.md`](examples/README.md).

Recommended order:

- `01_quickstart.py`
- `02_streaming_turn.py`
- `03_resume_thread.py`
- `04_multi_session.py`
- `05_approval_policy.py`
- `06_low_level_client.py`

From `python/`:

```bash
uv run python examples/01_quickstart.py
uv run python examples/02_streaming_turn.py
uv run python examples/03_resume_thread.py
uv run python examples/04_multi_session.py
uv run python examples/05_approval_policy.py
uv run python examples/06_low_level_client.py
```

## Development

From `python/`:

```bash
uv sync --dev
uv run python scripts/generate_protocol_client.py
uv run pytest -m "not integration"
uv run pytest -m integration
```

Integration tests expect a real local `codex` CLI installation and authenticated session.

## Notes and Constraints

- `Session.create(...)` defaults to spawning `codex app-server` over stdio via `StdioTransport`.
- The helper functions and enums are optional convenience layers; raw dict-based protocol access still works.
- Passing a custom `transport` and custom stdio launch options at the same time is rejected.
- The runtime defaults to `ApprovalPolicy.auto_decline()` unless you opt into another policy.
- `Turn` objects are async iterables for streaming consumption, and iteration is single-use.
- The package is repo-first today; this README documents source checkout usage rather than package registry installation.
