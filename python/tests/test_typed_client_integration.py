from __future__ import annotations

import asyncio
import shutil

import pytest

from codex_client import StdioTransport, TypedCodexClient

pytestmark = pytest.mark.integration


async def test_typed_client_reaches_turn_completion() -> None:
    if shutil.which("codex") is None:
        pytest.skip("codex CLI is not installed")

    client = TypedCodexClient.from_transport(StdioTransport())
    deltas: list[str] = []
    completed: asyncio.Future[dict[str, object]] = asyncio.get_running_loop().create_future()
    client.on_notification(
        "item/agentMessage/delta",
        lambda params: deltas.append(params["delta"]),
    )
    client.on_notification(
        "turn/completed",
        lambda params: completed.set_result(params) if not completed.done() else None,
    )

    try:
        await client.initialize({"clientInfo": {"name": "pytest", "version": "0.1.0"}})
        await client.send_initialized()

        thread = await client.thread_start({"ephemeral": True})
        thread_id = thread["thread"]["id"]

        turn = await client.turn_start(
            {
                "threadId": thread_id,
                "input": [{"type": "text", "text": "Reply with exactly OK."}],
            }
        )
        assert turn["turn"]["status"] == "inProgress"

        turn_completed = await asyncio.wait_for(completed, timeout=60.0)
        assert turn_completed["turn"]["status"] == "completed"
        assert "".join(deltas).strip() == "OK"
    finally:
        await client.close()
