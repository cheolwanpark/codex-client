from __future__ import annotations

import shutil

import pytest

from codex_client import ApprovalPolicy, Session

pytestmark = pytest.mark.integration


async def test_session_runtime_ask_reaches_turn_completion() -> None:
    if shutil.which("codex") is None:
        pytest.skip("codex CLI is not installed")

    async with await Session.create(
        client_info={"name": "pytest", "version": "0.1.0"},
        approval_policy=ApprovalPolicy.auto_accept(),
    ) as session:
        thread = await session.start_thread({"ephemeral": True})
        answer = await thread.ask("Reply with exactly OK.")
        assert answer.strip() == "OK"
