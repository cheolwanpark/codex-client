from __future__ import annotations

import asyncio
import shutil
from collections.abc import AsyncIterator

import pytest

from codex_client import ProtocolConnection, StdioTransport

pytestmark = pytest.mark.integration


async def wait_for_message(
    iterator: AsyncIterator[object],
    predicate,
    timeout: float,
):
    async def _read() -> object:
        while True:
            message = await anext(iterator)
            if predicate(message):
                return message

    return await asyncio.wait_for(_read(), timeout=timeout)


async def create_connection() -> ProtocolConnection:
    if shutil.which("codex") is None:
        pytest.skip("codex CLI is not installed")
    return ProtocolConnection(StdioTransport())


async def test_codex_requires_initialize_before_other_requests() -> None:
    connection = await create_connection()
    iterator = connection.__aiter__()

    try:
        await connection.send({"id": 1, "method": "thread/loaded/list", "params": {}})
        response = await wait_for_message(
            iterator,
            lambda message: isinstance(message, dict) and message.get("id") == 1,
            timeout=10.0,
        )
        assert response["error"]["code"] == -32600
        assert response["error"]["message"] == "Not initialized"

        await connection.send(
            {
                "id": 2,
                "method": "initialize",
                "params": {"clientInfo": {"name": "pytest", "version": "0.1.0"}},
            }
        )
        init_response = await wait_for_message(
            iterator,
            lambda message: isinstance(message, dict) and message.get("id") == 2,
            timeout=10.0,
        )
        assert "userAgent" in init_response["result"]

        await connection.send(
            {
                "id": 3,
                "method": "initialize",
                "params": {"clientInfo": {"name": "pytest", "version": "0.1.0"}},
            }
        )
        duplicate = await wait_for_message(
            iterator,
            lambda message: isinstance(message, dict) and message.get("id") == 3,
            timeout=10.0,
        )
        assert duplicate["error"]["code"] == -32600
        assert duplicate["error"]["message"] == "Already initialized"
    finally:
        await connection.close()


async def test_codex_experimental_api_and_thread_start() -> None:
    connection = await create_connection()
    iterator = connection.__aiter__()

    try:
        await connection.send(
            {
                "id": 1,
                "method": "initialize",
                "params": {
                    "clientInfo": {"name": "pytest", "version": "0.1.0"},
                    "capabilities": {"experimentalApi": True},
                },
            }
        )
        await wait_for_message(
            iterator,
            lambda message: isinstance(message, dict) and message.get("id") == 1,
            timeout=10.0,
        )
        await connection.send({"method": "initialized"})

        await connection.send({"id": 2, "method": "collaborationMode/list", "params": {}})
        collaboration = await wait_for_message(
            iterator,
            lambda message: isinstance(message, dict) and message.get("id") == 2,
            timeout=10.0,
        )
        modes = {entry["mode"] for entry in collaboration["result"]["data"]}
        assert {"plan", "default"} <= modes

        await connection.send({"id": 3, "method": "thread/start", "params": {"ephemeral": True}})
        response = await wait_for_message(
            iterator,
            lambda message: isinstance(message, dict) and message.get("id") == 3,
            timeout=15.0,
        )
        thread_id = response["result"]["thread"]["id"]

        started = await wait_for_message(
            iterator,
            lambda message: isinstance(message, dict)
            and message.get("method") == "thread/started"
            and message["params"]["thread"]["id"] == thread_id,
            timeout=15.0,
        )
        assert started["params"]["thread"]["id"] == thread_id
    finally:
        await connection.close()


async def test_codex_turn_start_reaches_completion() -> None:
    connection = await create_connection()
    iterator = connection.__aiter__()

    try:
        await connection.send(
            {
                "id": 1,
                "method": "initialize",
                "params": {
                    "clientInfo": {"name": "pytest", "version": "0.1.0"},
                    "capabilities": {"experimentalApi": True},
                },
            }
        )
        await wait_for_message(
            iterator,
            lambda message: isinstance(message, dict) and message.get("id") == 1,
            timeout=10.0,
        )
        await connection.send({"method": "initialized"})

        await connection.send({"id": 2, "method": "thread/start", "params": {"ephemeral": True}})
        thread_response = await wait_for_message(
            iterator,
            lambda message: isinstance(message, dict) and message.get("id") == 2,
            timeout=15.0,
        )
        thread_id = thread_response["result"]["thread"]["id"]

        await connection.send(
            {
                "id": 3,
                "method": "turn/start",
                "params": {
                    "threadId": thread_id,
                    "input": [{"type": "text", "text": "Reply with exactly OK."}],
                },
            }
        )
        turn_response = await wait_for_message(
            iterator,
            lambda message: isinstance(message, dict) and message.get("id") == 3,
            timeout=15.0,
        )
        assert turn_response["result"]["turn"]["status"] == "inProgress"

        agent_deltas: list[str] = []
        completed = await wait_for_message(
            iterator,
            lambda message: _capture_turn_completion(message, agent_deltas),
            timeout=60.0,
        )
        assert completed["params"]["turn"]["status"] == "completed"
        assert "".join(agent_deltas).strip() == "OK"
    finally:
        await connection.close()


def _capture_turn_completion(message: object, agent_deltas: list[str]) -> bool:
    if not isinstance(message, dict):
        return False

    if message.get("method") == "item/agentMessage/delta":
        agent_deltas.append(message["params"]["delta"])

    return message.get("method") == "turn/completed"
