from __future__ import annotations

import asyncio

from codex_harness_kit import StdioTransport, TypedCodexClient

from _common import CLIENT_INFO, print_section, require_codex_cli


async def main() -> None:
    require_codex_cli()
    print_section("Low-Level Typed Client")

    client = TypedCodexClient.from_transport(StdioTransport())
    completed: asyncio.Future[dict[str, object]] = asyncio.get_running_loop().create_future()
    deltas: list[str] = []

    client.on_notification(
        "item/agentMessage/delta",
        lambda params: deltas.append(params["delta"]) or print(params["delta"], end="", flush=True),
    )
    client.on_notification(
        "turn/completed",
        lambda params: completed.set_result(params) if not completed.done() else None,
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
                "input": [{"type": "text", "text": prompt}],
            }
        )
        print(f"Turn: {turn_response['turn']['id']}")
        print(f"Initial turn status: {turn_response['turn']['status']}")
        print("\nAgent stream:")

        turn_completed = await asyncio.wait_for(completed, timeout=60.0)
        print("\n")
        print(f"Completion status: {turn_completed['turn']['status']}")
        print(f"Buffered text: {''.join(deltas).strip()}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
