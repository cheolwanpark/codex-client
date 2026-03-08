from __future__ import annotations

import asyncio

from codex_harness_kit import ApprovalPolicy, Session

from _common import CLIENT_INFO, print_section, require_codex_cli


async def run_session(label: str, prompt: str) -> tuple[str, str, str]:
    async with await Session.create(
        client_info=CLIENT_INFO,
        approval_policy=ApprovalPolicy.auto_accept(),
    ) as session:
        thread = await session.start_ephemeral_thread()
        answer = await thread.ask(prompt)
        return label, thread.id, answer.strip()


async def main() -> None:
    require_codex_cli()
    print_section("Multiple Independent Sessions")
    print("Each session owns its own app-server connection and thread lifecycle.")

    results = await asyncio.gather(
        run_session("session-a", "Reply with exactly SESSION_A."),
        run_session("session-b", "Reply with exactly SESSION_B."),
    )

    for label, thread_id, answer in results:
        print(f"{label}: thread={thread_id} answer={answer}")

    print("\nThese sessions are independent. Use resume_thread(...) only when you want to reconnect to an existing persistent thread.")


if __name__ == "__main__":
    asyncio.run(main())
