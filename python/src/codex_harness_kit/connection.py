from __future__ import annotations

from collections.abc import AsyncIterator

from .codec import JsonRpcCodec
from .errors import JsonRpcCodecError, ProtocolStreamError
from .messages import JsonRpcMessage
from .transport import Transport


class ProtocolConnection:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    async def send(self, message: JsonRpcMessage) -> None:
        await self._transport.send(JsonRpcCodec.encode(message))

    def __aiter__(self) -> AsyncIterator[JsonRpcMessage]:
        return self._iterate()

    async def close(self) -> None:
        await self._transport.close()

    async def _iterate(self) -> AsyncIterator[JsonRpcMessage]:
        async for frame in self._transport:
            try:
                yield JsonRpcCodec.decode(frame)
            except JsonRpcCodecError as exc:
                raise ProtocolStreamError(
                    f"Failed to decode incoming JSON-RPC frame: {exc}"
                ) from exc
