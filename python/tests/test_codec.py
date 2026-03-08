from __future__ import annotations

import pytest

from codex_client import JsonRpcCodec, JsonRpcCodecError


def test_codec_round_trips_all_message_shapes() -> None:
    messages = [
        {
            "id": 1,
            "method": "initialize",
            "params": {"clientInfo": {"name": "test", "version": "0.1.0"}},
            "trace": {"traceparent": "abc"},
        },
        {"method": "initialized"},
        {"id": 2, "result": {"userAgent": "probe/1.0"}},
        {"id": 3, "error": {"code": -32600, "message": "Not initialized"}},
    ]

    for message in messages:
        encoded = JsonRpcCodec.encode(message)
        assert "\n" not in encoded
        assert JsonRpcCodec.decode(encoded) == message


def test_codec_accepts_explicit_jsonrpc_but_omits_it_on_encode() -> None:
    message = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"clientInfo": {"name": "test", "version": "0.1.0"}},
    }

    decoded = JsonRpcCodec.decode(
        '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"clientInfo":{"name":"test","version":"0.1.0"}}}'
    )

    assert decoded == message
    assert JsonRpcCodec.encode(decoded) == (
        '{"id":1,"method":"initialize","params":{"clientInfo":{"name":"test","version":"0.1.0"}}}'
    )


@pytest.mark.parametrize(
    ("frame", "message"),
    [
        ("{", "Invalid JSON"),
        ("[]", "JSON-RPC message must be an object"),
        ('{"result":{}}', "JSON-RPC response must include an id"),
        (
            '{"id":1,"method":"x","result":{}}',
            "JSON-RPC message cannot contain both method and result/error fields",
        ),
        (
            '{"id":1,"error":{"message":"oops"}}',
            "JSON-RPC error must include code and message",
        ),
        ('{"jsonrpc":"1.0","id":1,"result":{}}', 'JSON-RPC jsonrpc field must be exactly "2.0"'),
    ],
)
def test_codec_rejects_invalid_frames(frame: str, message: str) -> None:
    with pytest.raises(JsonRpcCodecError, match=message):
        JsonRpcCodec.decode(frame)


def test_codec_rejects_invalid_request_ids() -> None:
    with pytest.raises(JsonRpcCodecError, match="JSON-RPC id must be a string or integer"):
        JsonRpcCodec.encode({"id": True, "method": "initialize"})
