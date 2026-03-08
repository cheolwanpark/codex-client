from __future__ import annotations

import asyncio
import re
from collections.abc import AsyncIterator

import pytest

from codex_harness_kit import (
    JsonRpcCodec,
    MiddlewareAbortedError,
    ProtocolConnection,
    RequestTimeoutError,
    TypedCodexClient,
    UnknownResponseIdError,
)
from codex_harness_kit._generated import CLIENT_REQUEST_METHODS, CLIENT_REQUEST_METHOD_TO_PARAMS

_QUEUE_EOF = object()
_NULL_PARAM_METHODS = {
    "account/logout",
    "account/rateLimits/read",
    "config/mcpServer/reload",
    "configRequirements/read",
}


class MockTransport:
    def __init__(self) -> None:
        self.sent_frames: list[str] = []
        self.closed = False
        self._queue: asyncio.Queue[object] = asyncio.Queue()

    async def send(self, data: str) -> None:
        self.sent_frames.append(data)

    def __aiter__(self) -> AsyncIterator[str]:
        return self._iterate()

    async def close(self) -> None:
        self.closed = True
        await self._queue.put(_QUEUE_EOF)

    async def inject(self, message: object) -> None:
        if isinstance(message, str):
            await self._queue.put(message)
            return
        await self._queue.put(JsonRpcCodec.encode(message))

    async def fail(self, exc: BaseException) -> None:
        await self._queue.put(exc)

    async def next_sent(self) -> dict[str, object]:
        while not self.sent_frames:
            await asyncio.sleep(0)
        return JsonRpcCodec.decode(self.sent_frames.pop(0))

    async def _iterate(self) -> AsyncIterator[str]:
        while True:
            item = await self._queue.get()
            if item is _QUEUE_EOF:
                return
            if isinstance(item, BaseException):
                raise item
            yield str(item)


async def test_generated_wrappers_send_expected_methods_and_params() -> None:
    transport = MockTransport()
    client = TypedCodexClient(ProtocolConnection(transport))

    try:
        for method in CLIENT_REQUEST_METHODS:
            wrapper = getattr(client, _pythonize_method_name(method))
            task = asyncio.create_task(_call_wrapper(wrapper, method))
            sent = await transport.next_sent()

            assert sent["method"] == method
            if method in _NULL_PARAM_METHODS:
                assert sent["params"] is None
            elif CLIENT_REQUEST_METHOD_TO_PARAMS[method] == "InitializeParams":
                assert sent["params"] == {"clientInfo": {"name": "test", "version": "0.1.0"}}
            else:
                assert sent["params"] == {} or sent["params"] == {"probe": True}

            await transport.inject({"id": sent["id"], "result": {}})
            await task
    finally:
        await client.close()


async def test_client_matches_out_of_order_responses_by_request_id() -> None:
    transport = MockTransport()
    client = TypedCodexClient(ProtocolConnection(transport))

    try:
        first = asyncio.create_task(client.request("initialize", {"clientInfo": {"name": "one"}}))
        second = asyncio.create_task(client.request("thread/start", {"ephemeral": True}))

        first_sent = await transport.next_sent()
        second_sent = await transport.next_sent()

        await transport.inject({"id": second_sent["id"], "result": {"request": "second"}})
        await transport.inject({"id": first_sent["id"], "result": {"request": "first"}})

        assert await first == {"request": "first"}
        assert await second == {"request": "second"}
    finally:
        await client.close()


async def test_server_request_handler_returns_result() -> None:
    transport = MockTransport()
    client = TypedCodexClient(ProtocolConnection(transport))
    client.on_server_request(
        "item/commandExecution/requestApproval",
        lambda params: {"decision": "accept", "itemId": params["itemId"]},
    )

    try:
        await transport.inject(
            {
                "id": 9,
                "method": "item/commandExecution/requestApproval",
                "params": {"itemId": "item_1"},
            }
        )

        sent = await transport.next_sent()
        assert sent == {"id": 9, "result": {"decision": "accept", "itemId": "item_1"}}
    finally:
        await client.close()


async def test_missing_server_request_handler_returns_method_not_found() -> None:
    transport = MockTransport()
    client = TypedCodexClient(ProtocolConnection(transport))

    try:
        await transport.inject(
            {
                "id": 4,
                "method": "item/fileChange/requestApproval",
                "params": {"itemId": "item_1"},
            }
        )

        sent = await transport.next_sent()
        assert sent["id"] == 4
        assert sent["error"]["code"] == -32601
    finally:
        await client.close()


async def test_notification_handlers_fire_in_registration_order() -> None:
    transport = MockTransport()
    client = TypedCodexClient(ProtocolConnection(transport))
    calls: list[str] = []
    client.on_notification("thread/started", lambda params: calls.append(f"one:{params['thread']['id']}"))
    client.on_notification("thread/started", lambda params: calls.append(f"two:{params['thread']['id']}"))

    try:
        await transport.inject(
            {
                "method": "thread/started",
                "params": {"thread": {"id": "thr_1"}},
            }
        )
        await asyncio.sleep(0)
        assert calls == ["one:thr_1", "two:thr_1"]
    finally:
        await client.close()


async def test_middleware_runs_in_deterministic_order_for_outgoing_and_incoming() -> None:
    transport = MockTransport()
    client = TypedCodexClient(ProtocolConnection(transport))
    events: list[str] = []

    async def first(ctx, next_):
        events.append(f"before:first:{ctx.direction}:{ctx.method}")
        await next_()
        events.append(f"after:first:{ctx.direction}:{ctx.method}")

    async def second(ctx, next_):
        events.append(f"before:second:{ctx.direction}:{ctx.method}")
        await next_()
        events.append(f"after:second:{ctx.direction}:{ctx.method}")

    client.use(first).use(second)
    client.on_notification("thread/started", lambda params: events.append("notification"))

    try:
        request_task = asyncio.create_task(
            client.request("initialize", {"clientInfo": {"name": "test", "version": "0.1.0"}})
        )
        sent = await transport.next_sent()
        await transport.inject({"id": sent["id"], "result": {}})
        await request_task

        await transport.inject({"method": "thread/started", "params": {"thread": {"id": "thr_1"}}})
        await asyncio.sleep(0)

        assert events == [
            "before:first:outgoing:initialize",
            "before:second:outgoing:initialize",
            "after:second:outgoing:initialize",
            "after:first:outgoing:initialize",
            "before:first:incoming:None",
            "before:second:incoming:None",
            "after:second:incoming:None",
            "after:first:incoming:None",
            "before:first:incoming:thread/started",
            "before:second:incoming:thread/started",
            "notification",
            "after:second:incoming:thread/started",
            "after:first:incoming:thread/started",
        ]
    finally:
        await client.close()


async def test_outgoing_middleware_can_abort_request() -> None:
    transport = MockTransport()
    client = TypedCodexClient(ProtocolConnection(transport))

    async def abort(ctx, next_):
        if ctx.direction == "outgoing":
            return
        await next_()

    client.use(abort)

    try:
        with pytest.raises(MiddlewareAbortedError):
            await client.request("initialize", {"clientInfo": {"name": "test", "version": "0.1.0"}})
        assert transport.sent_frames == []
    finally:
        await client.close()


async def test_request_timeout_ignores_late_response() -> None:
    transport = MockTransport()
    client = TypedCodexClient(ProtocolConnection(transport))

    try:
        with pytest.raises(RequestTimeoutError):
            await client.request("initialize", {"clientInfo": {"name": "test"}}, timeout=0.01)

        timed_out_sent = await transport.next_sent()
        assert timed_out_sent["id"] == 0
        await transport.inject({"id": 0, "result": {"late": True}})

        follow_up = asyncio.create_task(client.request("thread/start", {"ephemeral": True}))
        sent = await transport.next_sent()
        await transport.inject({"id": sent["id"], "result": {"ok": True}})
        assert await follow_up == {"ok": True}
    finally:
        await client.close()


async def test_unknown_response_id_fails_pending_requests() -> None:
    transport = MockTransport()
    client = TypedCodexClient(ProtocolConnection(transport))

    try:
        pending = asyncio.create_task(client.request("initialize", {"clientInfo": {"name": "test"}}))
        await transport.next_sent()
        await transport.inject({"id": 999, "result": {}})

        with pytest.raises(UnknownResponseIdError):
            await pending
    finally:
        await client.close()


async def test_transport_failure_rejects_pending_requests() -> None:
    transport = MockTransport()
    client = TypedCodexClient(ProtocolConnection(transport))

    try:
        pending = asyncio.create_task(client.request("initialize", {"clientInfo": {"name": "test"}}))
        await transport.next_sent()
        await transport.fail(RuntimeError("transport blew up"))

        with pytest.raises(RuntimeError, match="transport blew up"):
            await pending
    finally:
        await client.close()


async def _call_wrapper(wrapper, method: str) -> object:
    if method in _NULL_PARAM_METHODS:
        return await wrapper()
    if CLIENT_REQUEST_METHOD_TO_PARAMS[method] == "InitializeParams":
        return await wrapper({"clientInfo": {"name": "test", "version": "0.1.0"}})
    if method in {"thread/start", "thread/list", "thread/loaded/list", "skills/list", "app/list"}:
        return await wrapper()
    return await wrapper({"probe": True})


def _pythonize_method_name(method: str) -> str:
    field = "_".join(segment for segment in re.split(r"[/\\-]", method) if segment)
    return re.sub(r"(?<!^)(?=[A-Z])", "_", field).lower()
