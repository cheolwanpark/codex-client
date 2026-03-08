from __future__ import annotations

import asyncio
from typing import Any

from codex_harness_kit import ApprovalPolicy, Session

from _common import CLIENT_INFO, print_section, require_codex_cli


async def on_command_execution(params: dict[str, Any]) -> dict[str, str]:
    print(f"command approval requested for item={params['itemId']}")
    return {"decision": "accept"}


async def on_file_change(params: dict[str, Any]) -> dict[str, str]:
    print(f"file change approval requested for item={params['itemId']}")
    return {"decision": "decline"}


async def on_tool_request_user_input(params: dict[str, Any]) -> dict[str, Any]:
    print(f"tool user input requested for item={params['itemId']}")
    answers = {
        question["id"]: {"answers": ["approved by host"]}
        for question in params["questions"]
    }
    return {"answers": answers}


async def on_dynamic_tool_call(params: dict[str, Any]) -> dict[str, Any]:
    print(f"dynamic tool call requested for call={params['callId']}")
    return {"success": False, "contentItems": []}


async def show_sample_hook_results(policy: ApprovalPolicy) -> None:
    print_section("Sample Hook Calls")
    print("These are local host-side demonstrations of the response shapes each hook returns.")

    command_result = await policy.handle_command_execution(
        {"threadId": "thr_demo", "turnId": "turn_demo", "itemId": "cmd_1"}
    )
    print(f"command result: {command_result}")

    file_result = await policy.handle_file_change(
        {"threadId": "thr_demo", "turnId": "turn_demo", "itemId": "file_1"}
    )
    print(f"file result: {file_result}")

    input_result = await policy.handle_tool_request_user_input(
        {
            "threadId": "thr_demo",
            "turnId": "turn_demo",
            "itemId": "input_1",
            "questions": [
                {
                    "id": "question_1",
                    "header": "Mode",
                    "question": "Proceed?",
                }
            ],
        }
    )
    print(f"tool input result: {input_result}")

    tool_result = await policy.handle_dynamic_tool_call(
        {
            "threadId": "thr_demo",
            "turnId": "turn_demo",
            "callId": "call_1",
            "tool": "demo",
            "arguments": {"probe": True},
        }
    )
    print(f"dynamic tool result: {tool_result}")


async def main() -> None:
    require_codex_cli()
    print_section("Custom Approval Policy")

    policy = ApprovalPolicy.custom(
        on_command_execution=on_command_execution,
        on_file_change=on_file_change,
        on_tool_request_user_input=on_tool_request_user_input,
        on_dynamic_tool_call=on_dynamic_tool_call,
    )

    print("This example uses explicit host hooks instead of the built-in auto-accept policy.")
    print("The default model for production code should stay fail-closed unless you opt in.")

    await show_sample_hook_results(policy)

    print_section("Attach Policy To Session")
    async with await Session.create(
        client_info=CLIENT_INFO,
        approval_policy=policy,
    ) as session:
        thread = await session.start_thread({"ephemeral": True})
        answer = await thread.ask("Reply with exactly OK.")
        print(f"Thread: {thread.id}")
        print(f"Answer: {answer.strip()}")
        print("This prompt does not need approvals, but the custom policy is now wired into the session.")


if __name__ == "__main__":
    asyncio.run(main())
