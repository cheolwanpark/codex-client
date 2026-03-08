from __future__ import annotations

import asyncio

from codex_harness_kit import ApprovalPolicy, Session

from _common import CLIENT_INFO, print_section, require_codex_cli


async def main() -> None:
    require_codex_cli()
    print_section("Resume Thread Across Sessions")

    async with await Session.create(
        client_info=CLIENT_INFO,
        approval_policy=ApprovalPolicy.auto_accept(),
    ) as first_session:
        thread = await first_session.start_thread({"ephemeral": False})
        first_answer = await thread.ask("Reply with exactly FIRST.")
        thread_id = thread.id

        print(f"Created persistent thread: {thread_id}")
        print(f"First answer: {first_answer.strip()}")

    print("Closed the first session. Reconnecting with a fresh session.")

    async with await Session.create(
        client_info=CLIENT_INFO,
        approval_policy=ApprovalPolicy.auto_accept(),
    ) as second_session:
        thread = await second_session.resume_thread(thread_id)
        snapshot = await second_session.read_thread(thread.id, include_turns=True)
        second_answer = await thread.ask("Reply with exactly SECOND.")

        print(f"Resumed thread: {thread.id}")
        print(f"Turns already on thread: {len(snapshot.get('turns', []))}")
        print(f"Second answer: {second_answer.strip()}")


if __name__ == "__main__":
    asyncio.run(main())
