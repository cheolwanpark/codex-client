from __future__ import annotations

from typing import NotRequired, TypeAlias, TypedDict

JSONScalar: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]
RequestId: TypeAlias = str | int


class W3cTraceContext(TypedDict, total=False):
    traceparent: str | None
    tracestate: str | None


class JsonRpcRequest(TypedDict, total=False):
    id: RequestId
    method: str
    params: NotRequired[JSONValue]
    trace: NotRequired[W3cTraceContext | None]
    jsonrpc: NotRequired[str]


class JsonRpcNotification(TypedDict, total=False):
    method: str
    params: NotRequired[JSONValue]
    jsonrpc: NotRequired[str]


class JsonRpcResponse(TypedDict, total=False):
    id: RequestId
    result: JSONValue
    jsonrpc: NotRequired[str]


class JsonRpcErrorObject(TypedDict, total=False):
    code: int
    message: str
    data: NotRequired[JSONValue]


class JsonRpcErrorResponse(TypedDict, total=False):
    id: RequestId
    error: JsonRpcErrorObject
    jsonrpc: NotRequired[str]


JsonRpcMessage: TypeAlias = (
    JsonRpcRequest | JsonRpcNotification | JsonRpcResponse | JsonRpcErrorResponse
)
