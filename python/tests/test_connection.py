from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

import pytest

from codex_client import JsonRpcCodec, ProtocolConnection, ProtocolStreamError

_QUEUE_EOF = object()


class FakeTransport:
    def __init__(self) -> None:
        self.sent: list[str] = []
        self.closed = False
        self._queue: asyncio.Queue[object] = asyncio.Queue()

    async def send(self, data: str) -> None:
        self.sent.append(data)

    def __aiter__(self) -> AsyncIterator[str]:
        return self._iterate()

    async def close(self) -> None:
        self.closed = True
        await self._queue.put(_QUEUE_EOF)

    async def inject(self, frame: str) -> None:
        await self._queue.put(frame)

    async def fail(self, exc: BaseException) -> None:
        await self._queue.put(exc)

    async def _iterate(self) -> AsyncIterator[str]:
        while True:
            item = await self._queue.get()
            if item is _QUEUE_EOF:
                return
            if isinstance(item, BaseException):
                raise item
            yield str(item)


async def test_connection_sends_compact_single_line_frames() -> None:
    transport = FakeTransport()
    connection = ProtocolConnection(transport)

    message = {
        "id": 1,
        "method": "initialize",
        "params": {"clientInfo": {"name": "probe", "version": "0.1.0"}},
    }
    await connection.send(message)

    assert transport.sent == [JsonRpcCodec.encode(message)]
    assert "\n" not in transport.sent[0]


async def test_connection_preserves_incoming_message_order() -> None:
    transport = FakeTransport()
    connection = ProtocolConnection(transport)
    iterator = connection.__aiter__()

    await transport.inject('{"id":1,"result":{"first":true}}')
    await transport.inject('{"id":2,"result":{"second":true}}')

    first = await anext(iterator)
    second = await anext(iterator)

    assert first["id"] == 1
    assert second["id"] == 2


async def test_connection_wraps_decode_failures() -> None:
    transport = FakeTransport()
    connection = ProtocolConnection(transport)
    iterator = connection.__aiter__()

    await transport.inject("{")

    with pytest.raises(ProtocolStreamError, match="Failed to decode incoming JSON-RPC frame"):
        await anext(iterator)


async def test_connection_propagates_transport_errors() -> None:
    transport = FakeTransport()
    connection = ProtocolConnection(transport)
    iterator = connection.__aiter__()

    await transport.fail(RuntimeError("transport blew up"))

    with pytest.raises(RuntimeError, match="transport blew up"):
        await anext(iterator)


async def test_connection_close_delegates_to_transport() -> None:
    transport = FakeTransport()
    connection = ProtocolConnection(transport)

    await connection.close()

    assert transport.closed is True
