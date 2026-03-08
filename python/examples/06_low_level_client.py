from __future__ import annotations

import asyncio

from codex_client import (
    NotificationMethod,
    StdioTransport,
    TypedCodexClient,
    text_input,
)

from _common import CLIENT_INFO, print_section, require_codex_cli


async def main() -> None:
    require_codex_cli()
    print_section("Low-Level Typed Client")

    client = TypedCodexClient.from_transport(StdioTransport())
    deltas: list[str] = []

    client.on_notification(
        NotificationMethod.ITEM_AGENT_MESSAGE_DELTA,
        lambda params: deltas.append(params["delta"]) or print(params["delta"], end="", flush=True),
    )

    try:
        await client.initialize({"clientInfo": CLIENT_INFO})
        await client.send_initialized()
        print("Initialized client and sent initialized notification.")

        thread_response = await client.thread_start({"ephemeral": True})
        thread_id = thread_response["thread"]["id"]
        print(f"Thread: {thread_id}")

        prompt = "Reply with exactly OK."
        turn_response = await client.turn_start(
            {
                "threadId": thread_id,
                "input": [text_input(prompt)],
            }
        )
        print(f"Turn: {turn_response['turn']['id']}")
        print(f"Initial turn status: {turn_response['turn']['status']}")
        print("\nAgent stream:")

        turn_completed = await client.wait_for_notification(
            NotificationMethod.TURN_COMPLETED,
            timeout=60.0,
        )
        print("\n")
        print(f"Completion status: {turn_completed['turn']['status']}")
        print(f"Buffered text: {''.join(deltas).strip()}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
