from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, cast

from .errors import JsonRpcCodecError
from .messages import JsonRpcErrorObject, JsonRpcErrorResponse, JsonRpcMessage


class JsonRpcCodec:
    @staticmethod
    def encode(message: JsonRpcMessage) -> str:
        normalized = _validate_message(message)
        payload = dict(normalized)
        payload.pop("jsonrpc", None)
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)

    @staticmethod
    def decode(frame: str) -> JsonRpcMessage:
        try:
            payload = json.loads(frame)
        except json.JSONDecodeError as exc:
            raise JsonRpcCodecError(f"Invalid JSON: {exc.msg}") from exc

        return _validate_message(payload)


def _validate_message(value: object) -> JsonRpcMessage:
    if not isinstance(value, Mapping):
        raise JsonRpcCodecError("JSON-RPC message must be an object")

    payload = dict(value)
    _validate_jsonrpc_field(payload)

    has_method = "method" in payload
    has_id = "id" in payload
    has_result = "result" in payload
    has_error = "error" in payload

    if has_method:
        if has_result or has_error:
            raise JsonRpcCodecError(
                "JSON-RPC message cannot contain both method and result/error fields"
            )

        method = payload["method"]
        if not isinstance(method, str):
            raise JsonRpcCodecError("JSON-RPC method must be a string")

        if has_id:
            _validate_request_id(payload["id"])
            _validate_trace(payload)
            return cast("JsonRpcMessage", payload)

        return cast("JsonRpcMessage", payload)

    if not has_id:
        raise JsonRpcCodecError("JSON-RPC response must include an id")

    _validate_request_id(payload["id"])

    if has_result == has_error:
        raise JsonRpcCodecError(
            "JSON-RPC response must contain exactly one of result or error"
        )

    if has_error:
        payload["error"] = _validate_error_object(payload["error"])

    return cast("JsonRpcMessage", payload)


def _validate_jsonrpc_field(payload: Mapping[str, object]) -> None:
    if "jsonrpc" not in payload:
        return

    if payload["jsonrpc"] != "2.0":
        raise JsonRpcCodecError('JSON-RPC jsonrpc field must be exactly "2.0"')


def _validate_request_id(value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise JsonRpcCodecError("JSON-RPC id must be a string or integer")


def _validate_trace(payload: Mapping[str, object]) -> None:
    if "trace" not in payload:
        return

    trace = payload["trace"]
    if trace is None:
        return

    if not isinstance(trace, Mapping):
        raise JsonRpcCodecError("JSON-RPC trace field must be an object or null")

    for key in ("traceparent", "tracestate"):
        if key in trace and trace[key] is not None and not isinstance(trace[key], str):
            raise JsonRpcCodecError(f"JSON-RPC trace.{key} must be a string or null")


def _validate_error_object(value: object) -> JsonRpcErrorObject:
    if not isinstance(value, Mapping):
        raise JsonRpcCodecError("JSON-RPC error must be an object")

    payload = dict(value)
    if "code" not in payload or "message" not in payload:
        raise JsonRpcCodecError("JSON-RPC error must include code and message")

    code = payload["code"]
    message = payload["message"]
    if isinstance(code, bool) or not isinstance(code, int):
        raise JsonRpcCodecError("JSON-RPC error code must be an integer")
    if not isinstance(message, str):
        raise JsonRpcCodecError("JSON-RPC error message must be a string")

    return cast(JsonRpcErrorObject, payload)
