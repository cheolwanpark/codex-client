# Codex Client (Unofficial)

Codex Client is a lightweight, community-maintained Python wrapper around the Codex CLI. It lets you launch chats, stream reasoning and tool events, and drive MCP servers from your own applications—similar to how the `claude-code-sdk` works for Anthropics' Claude tools, but tailored for Codex.

> This package is **not** an official OpenAI release. Expect the API surface to evolve as the Codex CLI changes.

## Installation

```bash
# clone this repository, then install in a virtual environment
pip install codex-client
# or, if you use uv
uv pip install codex-client
```

Ensure the `codex` executable is on your `PATH`, since the client shells out to `codex mcp serve` under the hood.

## Core Concepts

- **Client lifecycle** – `codex_sdk.Client` manages the background MCP session. Use it as an async context manager to guarantee clean startup and teardown.
- **Chats** – `codex_sdk.Chat` represents an ongoing conversation. Iterate over it for raw events, call `await chat.get()` for the final assistant reply, and `await chat.resume(...)` to continue the dialogue.
- **Configuration** – `CodexChatConfig`, `CodexProfile`, and `CodexMcpServer` (in `codex_sdk.config`) serialize options Codex expects: models, sandboxing, approval policy, working directory, environment overrides, MCP servers, and more.
- **Structured streaming** – Helpers in `codex_sdk.structured` (`structured`, `AssistantMessageStream`, `ReasoningStream`, `CommandStream`) aggregate low-level deltas into convenient async streams.
- **Events & errors** – All event dataclasses live in `codex_sdk.event`; exceptions (`CodexError`, `ChatError`, `ToolError`, etc.) live in `codex_sdk.exceptions` so you can handle failures precisely.

## Usage Example

```python
import asyncio
from codex_sdk import (
    Client,
    CodexChatConfig,
    CodexProfile,
    CodexMcpServer,
    ReasoningEffort,
    SandboxMode,
    Verbosity,
)
from codex_sdk.structured import structured, AssistantMessageStream, ReasoningStream, CommandStream

async def run(prompt: str) -> None:
    config = CodexChatConfig(
        profile=CodexProfile(
            model="gpt-5",
            reasoning_effort=ReasoningEffort.MINIMAL,
            verbosity=Verbosity.HIGH,
            sandbox=SandboxMode.DANGER_FULL_ACCESS,
        ),
        mcp_servers=[
            CodexMcpServer(
                name="context7",
                command="npx",
                args=["-y", "@upstash/context7-mcp", "--api-key", "<api_key>"]
            )
        ],
    )

    async with Client() as client:
        chat = await client.create_chat(prompt, config=config)

        async for event in structured(chat):
            if isinstance(event, AssistantMessageStream):
                async for chunk in event.stream():
                    print(chunk, end="", flush=True)
                print("\n[assistant message complete]")
            elif isinstance(event, ReasoningStream):
                async for chunk in event.stream():
                    print(f"[reasoning] {chunk}")
            elif isinstance(event, CommandStream):
                async for chunk in event.stream():
                    if chunk.text:
                        print(f"[command {event.command}] {chunk.text}")

        final_reply = await chat.get()
        print("Final reply:", final_reply)

        await chat.resume("Thanks! Any closing thoughts?")

asyncio.run(run("Introduce yourself."))
```

This pattern illustrates how to:

- Bootstrap a Codex profile, sandbox policy, and optional MCP servers.
- Open a chat, stream assistant output, reasoning traces, and command execution in real time.
- Retrieve the final assistant response and continue the conversation with `chat.resume()`.

## Extending Codex Client

- Inject your own MCP servers or tools by modifying the `CodexChatConfig` you pass to `Client.create_chat`.
- Capture richer telemetry (token counts, command durations, event payloads) by iterating the raw `chat` events instead of the structured helper.
- Integrate Codex Client into automation (FastAPI endpoints, Slack bots, GitHub Actions) so Codex handles the heavy lifting while you orchestrate workflows.

Bug reports and contributions are welcome—the codebase stays intentionally small so you can adapt it quickly.
