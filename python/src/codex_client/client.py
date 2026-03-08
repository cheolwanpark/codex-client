from __future__ import annotations

import asyncio
import contextlib
import time
from collections import defaultdict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Literal, TypeAlias

from ._generated import SERVER_NOTIFICATION_METHODS, SERVER_REQUEST_METHODS
from ._generated_client import GeneratedClientMixin
from .connection import ProtocolConnection
from .errors import (
    ClientClosedError,
    MiddlewareAbortedError,
    ProtocolClientError,
    RequestTimeoutError,
    UnknownResponseIdError,
)
from .messages import JSONValue, JsonRpcErrorObject, JsonRpcMessage, RequestId
from .transport import Transport

MiddlewareDirection: TypeAlias = Literal["incoming", "outgoing"]


@dataclass(slots=True)
class MiddlewareContext:
    message: JsonRpcMessage
    direction: MiddlewareDirection
    method: str | None
    request_id: RequestId | None
    timestamp: float
    client: "TypedCodexClient"


MiddlewareNext: TypeAlias = Callable[[], Awaitable[None]]
Middleware: TypeAlias = Callable[[MiddlewareContext, MiddlewareNext], Awaitable[None]]
ServerRequestHandler: TypeAlias = Callable[[JSONValue], Awaitable[JSONValue] | JSONValue]
NotificationHandler: TypeAlias = Callable[[JSONValue], Awaitable[None] | None]
NotificationPredicate: TypeAlias = Callable[[JSONValue], bool]


class TypedCodexClient(GeneratedClientMixin):
    def __init__(self, connection: ProtocolConnection) -> None:
        self._connection = connection
        self._middleware: list[Middleware] = []
        self._pending_requests: dict[RequestId, asyncio.Future[JSONValue]] = {}
        self._timed_out_request_ids: set[RequestId] = set()
        self._server_request_handlers: dict[str, ServerRequestHandler] = {}
        self._notification_handlers: defaultdict[str, list[NotificationHandler]] = defaultdict(list)
        self._next_request_id = 0
        self._closed = False
        self._fatal_error: Exception | None = None
        self._reader_task = asyncio.create_task(self._reader_loop())

    @classmethod
    def from_transport(cls, transport: Transport) -> "TypedCodexClient":
        return cls(ProtocolConnection(transport))

    def use(self, middleware: Middleware) -> "TypedCodexClient":
        self._middleware.append(middleware)
        return self

    def on_server_request(
        self, method: str, handler: ServerRequestHandler
    ) -> Callable[[], None]:
        self._server_request_handlers[method] = handler

        def unsubscribe() -> None:
            current = self._server_request_handlers.get(method)
            if current is handler:
                self._server_request_handlers.pop(method, None)

        return unsubscribe

    def on_notification(
        self, method: str, handler: NotificationHandler
    ) -> Callable[[], None]:
        handlers = self._notification_handlers[method]
        handlers.append(handler)

        def unsubscribe() -> None:
            with contextlib.suppress(ValueError):
                handlers.remove(handler)

        return unsubscribe

    def off(self, method: str) -> "TypedCodexClient":
        self._server_request_handlers.pop(method, None)
        self._notification_handlers.pop(method, None)
        return self

    async def request(
        self, method: str, params: JSONValue | None = None, *, timeout: float | None = None
    ) -> JSONValue:
        self._ensure_open()

        request_id = self._allocate_request_id()
        future: asyncio.Future[JSONValue] = asyncio.get_running_loop().create_future()
        self._pending_requests[request_id] = future
        message: JsonRpcMessage = {
            "id": request_id,
            "method": method,
            "params": params,
        }

        try:
            delivered = await self._run_middleware(
                message, direction="outgoing", terminal=self._send_terminal
            )
            if not delivered:
                raise MiddlewareAbortedError(
                    f'Outgoing request "{method}" was aborted by middleware'
                )
        except Exception:
            self._pending_requests.pop(request_id, None)
            raise

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError as exc:
            self._pending_requests.pop(request_id, None)
            self._timed_out_request_ids.add(request_id)
            raise RequestTimeoutError(
                f'JSON-RPC request "{method}" timed out after {timeout} seconds'
            ) from exc

    async def notify(self, method: str, params: JSONValue | None = None) -> None:
        self._ensure_open()
        message: JsonRpcMessage = {"method": method}
        if params is not None:
            message["params"] = params

        await self._run_middleware(message, direction="outgoing", terminal=self._send_terminal)

    async def send_initialized(self) -> None:
        await self.notify("initialized")

    async def wait_for_notification(
        self,
        method: str,
        *,
        predicate: NotificationPredicate | None = None,
        timeout: float | None = None,
    ) -> JSONValue:
        self._ensure_open()

        future: asyncio.Future[JSONValue] = asyncio.get_running_loop().create_future()

        def handler(params: JSONValue) -> None:
            if predicate is not None and not predicate(params):
                return
            if not future.done():
                future.set_result(params)

        unsubscribe = self.on_notification(method, handler)
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError as exc:
            raise RequestTimeoutError(
                f'Notification "{method}" timed out after {timeout} seconds'
            ) from exc
        finally:
            unsubscribe()

    async def close(self) -> None:
        if self._closed:
            return

        self._closed = True
        self._fail_pending_requests(ClientClosedError("TypedCodexClient is closed"))
        self._reader_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._reader_task
        await self._connection.close()

    async def _reader_loop(self) -> None:
        try:
            async for message in self._connection:
                await self._run_middleware(
                    message, direction="incoming", terminal=self._dispatch_terminal
                )
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self._fatal_error = exc
            self._fail_pending_requests(exc)

    async def _run_middleware(
        self,
        message: JsonRpcMessage,
        *,
        direction: MiddlewareDirection,
        terminal: Callable[[MiddlewareContext], Awaitable[None]],
    ) -> bool:
        context = MiddlewareContext(
            message=message,
            direction=direction,
            method=message.get("method"),
            request_id=message.get("id"),
            timestamp=time.time(),
            client=self,
        )
        delivered = False

        async def call_chain(index: int) -> None:
            nonlocal delivered
            if index == len(self._middleware):
                delivered = True
                await terminal(context)
                return

            middleware = self._middleware[index]
            await middleware(context, lambda: call_chain(index + 1))

        await call_chain(0)
        return delivered

    async def _send_terminal(self, context: MiddlewareContext) -> None:
        await self._connection.send(context.message)

    async def _dispatch_terminal(self, context: MiddlewareContext) -> None:
        await self._dispatch_incoming_message(context.message)

    async def _dispatch_incoming_message(self, message: JsonRpcMessage) -> None:
        if self._is_response(message):
            self._handle_response(message)
            return
        if self._is_request(message):
            await self._handle_server_request(message)
            return
        if self._is_notification(message):
            await self._handle_notification(message)

    def _handle_response(self, message: JsonRpcMessage) -> None:
        request_id = message["id"]
        future = self._pending_requests.pop(request_id, None)
        if future is None:
            if request_id in self._timed_out_request_ids:
                self._timed_out_request_ids.discard(request_id)
                return
            raise UnknownResponseIdError(
                f"Received response for unknown request id {request_id!r}"
            )

        if "error" in message:
            future.set_exception(self._json_rpc_error_to_exception(message["error"]))
            return

        future.set_result(message.get("result"))

    async def _handle_server_request(self, message: JsonRpcMessage) -> None:
        method = message["method"]
        request_id = message["id"]
        params = message.get("params")
        handler = self._server_request_handlers.get(method)

        if method not in SERVER_REQUEST_METHODS or handler is None:
            await self._send_error_response(
                request_id,
                code=-32601,
                message=f'No server request handler registered for "{method}"',
            )
            return

        try:
            result = handler(params)
            if asyncio.iscoroutine(result):
                result = await result
        except Exception as exc:
            await self._send_error_response(
                request_id,
                code=-32000,
                message=str(exc) or "Server request handler failed",
            )
            return

        response: JsonRpcMessage = {"id": request_id, "result": result}
        delivered = await self._run_middleware(
            response, direction="outgoing", terminal=self._send_terminal
        )
        if not delivered:
            raise MiddlewareAbortedError(
                f'Outgoing response for server request "{method}" was aborted by middleware'
            )

    async def _handle_notification(self, message: JsonRpcMessage) -> None:
        method = message["method"]
        if method not in SERVER_NOTIFICATION_METHODS:
            return

        for handler in list(self._notification_handlers.get(method, [])):
            result = handler(message.get("params"))
            if asyncio.iscoroutine(result):
                await result

    async def _send_error_response(
        self, request_id: RequestId, *, code: int, message: str
    ) -> None:
        error_message: JsonRpcMessage = {
            "id": request_id,
            "error": {"code": code, "message": message},
        }
        delivered = await self._run_middleware(
            error_message, direction="outgoing", terminal=self._send_terminal
        )
        if not delivered:
            raise MiddlewareAbortedError(
                f"Outgoing error response for request id {request_id!r} was aborted by middleware"
            )

    def _fail_pending_requests(self, exc: Exception) -> None:
        pending = list(self._pending_requests.values())
        self._pending_requests.clear()
        for future in pending:
            if not future.done():
                future.set_exception(exc)

    def _ensure_open(self) -> None:
        if self._closed:
            raise ClientClosedError("TypedCodexClient is closed")
        if self._fatal_error is not None:
            raise self._fatal_error

    def _allocate_request_id(self) -> int:
        request_id = self._next_request_id
        self._next_request_id += 1
        return request_id

    def _json_rpc_error_to_exception(
        self, error: JsonRpcErrorObject | None
    ) -> ProtocolClientError:
        if not error:
            return ProtocolClientError("JSON-RPC request failed")
        return ProtocolClientError(
            f'{error.get("message", "JSON-RPC request failed")} (code: {error.get("code")})'
        )

    def _is_request(self, message: JsonRpcMessage) -> bool:
        return "method" in message and "id" in message

    def _is_notification(self, message: JsonRpcMessage) -> bool:
        return "method" in message and "id" not in message

    def _is_response(self, message: JsonRpcMessage) -> bool:
        return "id" in message and ("result" in message or "error" in message)
