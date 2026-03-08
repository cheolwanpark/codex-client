from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from codex_client import JsonRpcCodec

_QUEUE_EOF = object()


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
