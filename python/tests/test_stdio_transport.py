from __future__ import annotations

import asyncio
import pathlib
import sys

import pytest

from codex_harness_kit import ProtocolStreamError, StdioTransport


HELPER = pathlib.Path(__file__).parent / "helpers" / "stdio_child.py"


async def test_stdio_transport_round_trips_single_line_frames() -> None:
    transport = StdioTransport(command=sys.executable, args=(str(HELPER), "echo"))
    iterator = transport.__aiter__()

    try:
        await transport.send('{"id":1,"result":{"ok":true}}')
        frame = await asyncio.wait_for(anext(iterator), timeout=5.0)
        assert frame == '{"id":1,"result":{"ok":true}}'
    finally:
        await transport.close()


async def test_stdio_transport_rejects_multiline_frames() -> None:
    transport = StdioTransport(command=sys.executable, args=(str(HELPER), "echo"))

    try:
        with pytest.raises(ValueError, match="single line"):
            await transport.send('{"id":1}\n{"id":2}')
    finally:
        await transport.close()


async def test_stdio_transport_reports_child_exit_with_stderr_tail() -> None:
    transport = StdioTransport(
        command=sys.executable,
        args=(str(HELPER), "crash-after-first-line"),
    )
    iterator = transport.__aiter__()

    try:
        await transport.send('{"id":1,"result":{"ok":true}}')
        with pytest.raises(ProtocolStreamError, match="child saw line before crash"):
            await asyncio.wait_for(anext(iterator), timeout=5.0)
    finally:
        await transport.close()


async def test_stdio_transport_honors_cwd() -> None:
    transport = StdioTransport(
        command=sys.executable,
        args=(str(HELPER), "emit-path-and-exit"),
        cwd=str(pathlib.Path(__file__).parent),
    )
    iterator = transport.__aiter__()

    try:
        frame = await asyncio.wait_for(anext(iterator), timeout=5.0)
        assert frame == str(pathlib.Path(__file__).parent)
    finally:
        await transport.close()
