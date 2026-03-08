from __future__ import annotations

import asyncio

import pytest

from codex_harness_kit import ApprovalPolicy, Session
from tests.helpers.mock_transport import MockTransport


async def test_session_create_initializes_and_closes_cleanly() -> None:
    transport = MockTransport()
    session = await create_session(transport)

    try:
        assert session.client is not None
    finally:
        await session.close()

    assert transport.closed is True


async def test_session_create_rejects_transport_with_custom_stdio_options() -> None:
    with pytest.raises(ValueError):
        await Session.create(
            client_info={"name": "pytest", "version": "0.1.0"},
            transport=MockTransport(),
            cwd="/tmp/project",
        )


async def test_thread_wrappers_are_reused_for_same_thread_id() -> None:
    transport = MockTransport()
    session = await create_session(transport)

    try:
        start_task = asyncio.create_task(session.start_thread({"ephemeral": True}))
        sent = await transport.next_sent()
        assert sent["method"] == "thread/start"
        await transport.inject({"id": sent["id"], "result": {"thread": make_thread("thr_1")}})
        thread = await start_task

        resume_task = asyncio.create_task(session.resume_thread("thr_1"))
        sent = await transport.next_sent()
        assert sent["method"] == "thread/resume"
        await transport.inject(
            {
                "id": sent["id"],
                "result": {
                    "thread": make_thread("thr_1", name="Renamed"),
                    "approvalPolicy": "never",
                    "cwd": "/tmp",
                    "model": "gpt-5.1-codex",
                    "modelProvider": "openai",
                    "sandbox": {"type": "readOnly"},
                },
            }
        )
        resumed = await resume_task

        assert resumed is thread
        assert thread.name == "Renamed"
    finally:
        await session.close()


async def test_thread_notifications_update_runtime_state_and_emit_raw_handlers() -> None:
    transport = MockTransport()
    session = await create_session(transport)

    try:
        thread = await start_thread(session, transport)
        session_events: list[dict[str, object]] = []
        thread_events: list[dict[str, object]] = []
        session.on("thread/status/changed", lambda params: session_events.append(params))
        thread.on("thread/name/updated", lambda params: thread_events.append(params))

        await transport.inject(
            {
                "method": "thread/status/changed",
                "params": {"threadId": thread.id, "status": {"type": "active", "activeFlags": []}},
            }
        )
        await transport.inject(
            {
                "method": "thread/name/updated",
                "params": {"threadId": thread.id, "threadName": "Updated Name"},
            }
        )
        await asyncio.sleep(0)

        assert thread.status == {"type": "active", "activeFlags": []}
        assert thread.name == "Updated Name"
        assert session_events == [{"threadId": thread.id, "status": {"type": "active", "activeFlags": []}}]
        assert thread_events == [{"threadId": thread.id, "threadName": "Updated Name"}]
    finally:
        await session.close()


async def test_turn_stream_buffers_events_updates_state_and_returns_text() -> None:
    transport = MockTransport()
    session = await create_session(transport)

    try:
        thread = await start_thread(session, transport)
        turn_task = asyncio.create_task(thread.start_turn("Reply with hello"))
        sent = await transport.next_sent()
        assert sent["method"] == "turn/start"
        assert sent["params"]["input"] == [{"type": "text", "text": "Reply with hello"}]
        await transport.inject({"id": sent["id"], "result": {"turn": make_turn("turn_1")}})
        turn = await turn_task

        await transport.inject(
            {
                "method": "item/started",
                "params": {
                    "threadId": thread.id,
                    "turnId": turn.id,
                    "item": {"id": "item_1", "type": "agentMessage", "text": ""},
                },
            }
        )
        await transport.inject(
            {
                "method": "item/agentMessage/delta",
                "params": {"threadId": thread.id, "turnId": turn.id, "itemId": "item_1", "delta": "Hel"},
            }
        )
        await transport.inject(
            {
                "method": "item/agentMessage/delta",
                "params": {"threadId": thread.id, "turnId": turn.id, "itemId": "item_1", "delta": "lo"},
            }
        )
        await transport.inject(
            {
                "method": "turn/plan/updated",
                "params": {
                    "threadId": thread.id,
                    "turnId": turn.id,
                    "explanation": "Plan changed",
                    "plan": [{"step": "reply", "status": "completed"}],
                },
            }
        )
        await transport.inject(
            {
                "method": "turn/completed",
                "params": {
                    "threadId": thread.id,
                    "turn": make_turn(
                        "turn_1",
                        status="completed",
                        items=[{"id": "item_1", "type": "agentMessage", "text": "Hello"}],
                    ),
                },
            }
        )

        events = [event async for event in turn]

        assert [event["type"] for event in events] == [
            "item_started",
            "agent_message_delta",
            "agent_message_delta",
            "plan_updated",
            "completed",
        ]
        assert turn.items == [{"id": "item_1", "type": "agentMessage", "text": "Hello"}]
        assert await turn.text() == "Hello"
    finally:
        await session.close()


async def test_turn_iteration_is_single_use() -> None:
    transport = MockTransport()
    session = await create_session(transport)

    try:
        thread = await start_thread(session, transport)
        turn = await start_turn(thread, transport, "stream once")
        iterator = turn.__aiter__()

        with pytest.raises(RuntimeError):
            turn.__aiter__()

        await transport.inject(
            {
                "method": "turn/completed",
                "params": {
                    "threadId": thread.id,
                    "turn": make_turn("turn_1", status="completed"),
                },
            }
        )

        events = [event async for event in iterator]
        assert events[-1]["type"] == "completed"
    finally:
        await session.close()


async def test_turn_mutates_reasoning_and_command_items_from_deltas() -> None:
    transport = MockTransport()
    session = await create_session(transport)

    try:
        thread = await start_thread(session, transport)
        turn = await start_turn(thread, transport, "explain")

        await transport.inject(
            {
                "method": "item/reasoning/textDelta",
                "params": {
                    "threadId": thread.id,
                    "turnId": turn.id,
                    "itemId": "reason_1",
                    "contentIndex": 0,
                    "delta": "Think",
                },
            }
        )
        await transport.inject(
            {
                "method": "item/reasoning/summaryTextDelta",
                "params": {
                    "threadId": thread.id,
                    "turnId": turn.id,
                    "itemId": "reason_1",
                    "summaryIndex": 0,
                    "delta": "Summary",
                },
            }
        )
        await transport.inject(
            {
                "method": "item/commandExecution/outputDelta",
                "params": {
                    "threadId": thread.id,
                    "turnId": turn.id,
                    "itemId": "cmd_1",
                    "delta": "stdout",
                },
            }
        )
        await asyncio.sleep(0)

        assert turn.items[0] == {
            "id": "reason_1",
            "type": "reasoning",
            "summary": ["Summary"],
            "content": ["Think"],
        }
        assert turn.items[1] == {
            "id": "cmd_1",
            "type": "commandExecution",
            "command": "",
            "commandActions": [],
            "cwd": "",
            "status": "inProgress",
            "aggregatedOutput": "stdout",
        }
    finally:
        await session.close()


async def test_ask_returns_final_agent_text() -> None:
    transport = MockTransport()
    session = await create_session(transport)

    try:
        thread = await start_thread(session, transport)
        ask_task = asyncio.create_task(thread.ask("Reply with OK"))
        sent = await transport.next_sent()
        await transport.inject({"id": sent["id"], "result": {"turn": make_turn("turn_1")}})
        await transport.inject(
            {
                "method": "turn/completed",
                "params": {
                    "threadId": thread.id,
                    "turn": make_turn(
                        "turn_1",
                        status="completed",
                        items=[{"id": "item_1", "type": "agentMessage", "text": "OK"}],
                    ),
                },
            }
        )

        assert await ask_task == "OK"
    finally:
        await session.close()


async def test_approval_policy_handles_all_supported_server_requests() -> None:
    transport = MockTransport()
    policy_calls: list[tuple[str, str]] = []
    session = await create_session(
        transport,
        approval_policy=ApprovalPolicy.custom(
            on_command_execution=lambda params: _record_call(
                policy_calls, "command", params["itemId"], {"decision": "accept"}
            ),
            on_file_change=lambda params: _record_call(
                policy_calls, "file", params["itemId"], {"decision": "acceptForSession"}
            ),
            on_tool_request_user_input=lambda params: _record_call(
                policy_calls,
                "input",
                params["itemId"],
                {"answers": {"question_1": {"answers": ["yes"]}}},
            ),
            on_dynamic_tool_call=lambda params: _record_call(
                policy_calls,
                "tool",
                params["callId"],
                {"success": True, "contentItems": [{"type": "inputText", "text": "tool output"}]},
            ),
        ),
    )

    try:
        await transport.inject(
            {
                "id": 10,
                "method": "item/commandExecution/requestApproval",
                "params": {"threadId": "thr_1", "turnId": "turn_1", "itemId": "cmd_1"},
            }
        )
        assert await transport.next_sent() == {"id": 10, "result": {"decision": "accept"}}

        await transport.inject(
            {
                "id": 11,
                "method": "item/fileChange/requestApproval",
                "params": {"threadId": "thr_1", "turnId": "turn_1", "itemId": "file_1"},
            }
        )
        assert await transport.next_sent() == {
            "id": 11,
            "result": {"decision": "acceptForSession"},
        }

        await transport.inject(
            {
                "id": 12,
                "method": "item/tool/requestUserInput",
                "params": {
                    "threadId": "thr_1",
                    "turnId": "turn_1",
                    "itemId": "input_1",
                    "questions": [{"id": "question_1", "header": "H", "question": "Q"}],
                },
            }
        )
        assert await transport.next_sent() == {
            "id": 12,
            "result": {"answers": {"question_1": {"answers": ["yes"]}}},
        }

        await transport.inject(
            {
                "id": 13,
                "method": "item/tool/call",
                "params": {
                    "threadId": "thr_1",
                    "turnId": "turn_1",
                    "callId": "call_1",
                    "tool": "demo",
                    "arguments": {"probe": True},
                },
            }
        )
        assert await transport.next_sent() == {
            "id": 13,
            "result": {
                "success": True,
                "contentItems": [{"type": "inputText", "text": "tool output"}],
            },
        }

        assert policy_calls == [
            ("command", "cmd_1"),
            ("file", "file_1"),
            ("input", "input_1"),
            ("tool", "call_1"),
        ]
    finally:
        await session.close()


async def test_default_policy_is_fail_closed() -> None:
    transport = MockTransport()
    session = await create_session(transport)

    try:
        await transport.inject(
            {
                "id": 20,
                "method": "item/commandExecution/requestApproval",
                "params": {"threadId": "thr_1", "turnId": "turn_1", "itemId": "cmd_1"},
            }
        )
        assert await transport.next_sent() == {"id": 20, "result": {"decision": "decline"}}

        await transport.inject(
            {
                "id": 21,
                "method": "item/tool/call",
                "params": {
                    "threadId": "thr_1",
                    "turnId": "turn_1",
                    "callId": "call_1",
                    "tool": "demo",
                    "arguments": {},
                },
            }
        )
        assert await transport.next_sent() == {
            "id": 21,
            "result": {"success": False, "contentItems": []},
        }
    finally:
        await session.close()


async def create_session(
    transport: MockTransport, approval_policy: ApprovalPolicy | None = None
) -> Session:
    task = asyncio.create_task(
        Session.create(
            client_info={"name": "pytest", "version": "0.1.0"},
            transport=transport,
            approval_policy=approval_policy,
        )
    )
    initialize = await transport.next_sent()
    assert initialize["method"] == "initialize"
    await transport.inject({"id": initialize["id"], "result": {"userAgent": "pytest"}})
    initialized = await transport.next_sent()
    assert initialized == {"method": "initialized"}
    return await task


async def start_thread(session: Session, transport: MockTransport):
    task = asyncio.create_task(session.start_thread({"ephemeral": True}))
    sent = await transport.next_sent()
    await transport.inject(
        {
            "id": sent["id"],
            "result": {
                "thread": make_thread("thr_1"),
                "approvalPolicy": "never",
                "cwd": "/tmp",
                "model": "gpt-5.1-codex",
                "modelProvider": "openai",
                "sandbox": {"type": "readOnly"},
            },
        }
    )
    return await task


async def start_turn(thread, transport: MockTransport, text: str):
    task = asyncio.create_task(thread.start_turn(text))
    sent = await transport.next_sent()
    await transport.inject({"id": sent["id"], "result": {"turn": make_turn("turn_1")}})
    return await task


def make_thread(thread_id: str, *, name: str | None = None) -> dict[str, object]:
    return {
        "id": thread_id,
        "cliVersion": "0.1.0",
        "createdAt": 0,
        "cwd": "/tmp",
        "ephemeral": True,
        "modelProvider": "openai",
        "name": name,
        "preview": "",
        "source": "appServer",
        "status": {"type": "idle"},
        "turns": [],
        "updatedAt": 0,
    }


def make_turn(
    turn_id: str,
    *,
    status: str = "inProgress",
    items: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    return {"id": turn_id, "status": status, "items": items or [], "error": None}


def _record_call(calls, kind: str, identifier: str, response):
    calls.append((kind, identifier))
    return response
