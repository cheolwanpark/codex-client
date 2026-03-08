from __future__ import annotations

import asyncio

from codex_harness_kit import ApprovalPolicy, Session, TurnEventType

from _common import CLIENT_INFO, print_section, require_codex_cli


async def main() -> None:
    require_codex_cli()
    print_section("Streaming Turn Events")

    async with await Session.create(
        client_info=CLIENT_INFO,
        approval_policy=ApprovalPolicy.auto_accept(),
    ) as session:
        thread = await session.start_ephemeral_thread()
        prompt = "Plan a short explanation of this SDK, then explain it in one paragraph."
        turn = await thread.start_turn(prompt)
        saw_plan_update = False

        print(f"Thread: {thread.id}")
        print(f"Turn: {turn.id}")
        print(f"Prompt: {prompt}")
        print("\nAgent stream:")

        async for event in turn:
            if event["type"] == TurnEventType.AGENT_MESSAGE_DELTA:
                print(event["delta"], end="", flush=True)
            elif event["type"] == TurnEventType.PLAN_UPDATED:
                saw_plan_update = True
                print("\n\n[plan_updated]")
                if event["explanation"] is not None:
                    print(f"Explanation: {event['explanation']}")
                for step in event["plan"]:
                    print(f"- {step['status']}: {step['step']}")
            elif event["type"] == TurnEventType.COMPLETED:
                print(f"\n\n[completed] status={event['turn']['status']}")

        if not saw_plan_update:
            print("\n[no plan updates were emitted for this prompt]")

        print_section("Buffered Final Text")
        print((await turn.text()).strip())


if __name__ == "__main__":
    asyncio.run(main())
