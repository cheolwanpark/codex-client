from __future__ import annotations

import asyncio

from codex_harness_kit import ApprovalPolicy, Session

from _common import CLIENT_INFO, print_section, require_codex_cli


async def main() -> None:
    require_codex_cli()
    print_section("Quickstart")

    async with await Session.create(
        client_info=CLIENT_INFO,
        approval_policy=ApprovalPolicy.auto_accept(),
    ) as session:
        thread = await session.start_thread({"ephemeral": True})
        prompt = "Reply with exactly OK."

        print(f"Thread: {thread.id}")
        print(f"Prompt: {prompt}")

        answer = await thread.ask(prompt)
        print(f"Answer: {answer.strip()}")


if __name__ == "__main__":
    asyncio.run(main())
