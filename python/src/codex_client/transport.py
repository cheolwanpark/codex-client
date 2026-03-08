from __future__ import annotations

import asyncio
import os
from collections import deque
from collections.abc import AsyncIterator, Mapping, Sequence
from typing import Protocol, runtime_checkable

from .errors import ProtocolStreamError, TransportClosedError

_QUEUE_EOF = object()


@runtime_checkable
class Transport(Protocol):
    async def send(self, data: str) -> None: ...

    def __aiter__(self) -> AsyncIterator[str]: ...

    async def close(self) -> None: ...


class StdioTransport:
    def __init__(
        self,
        command: str = "codex",
        args: Sequence[str] = ("app-server",),
        cwd: str | None = None,
        env: Mapping[str, str] | None = None,
    ) -> None:
        self._command = command
        self._args = tuple(args)
        self._cwd = cwd
        self._env = dict(env) if env is not None else None
        self._stderr_tail: deque[str] = deque(maxlen=50)
        self._queue: asyncio.Queue[object] = asyncio.Queue()
        self._process: asyncio.subprocess.Process | None = None
        self._stdout_task: asyncio.Task[None] | None = None
        self._stderr_task: asyncio.Task[None] | None = None
        self._start_lock = asyncio.Lock()
        self._close_lock = asyncio.Lock()
        self._closed = False

    async def __aenter__(self) -> "StdioTransport":
        await self._ensure_started()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def send(self, data: str) -> None:
        if "\n" in data or "\r" in data:
            raise ValueError("StdioTransport.send expects a single line without newlines")

        await self._ensure_started()

        if self._closed:
            raise TransportClosedError("Transport is closed")

        process = self._require_process()
        if process.stdin is None:
            raise TransportClosedError("Transport stdin is not available")

        try:
            process.stdin.write(f"{data}\n".encode("utf-8"))
            await process.stdin.drain()
        except (BrokenPipeError, ConnectionResetError) as exc:
            raise TransportClosedError("Transport stdin is closed") from exc

    def __aiter__(self) -> AsyncIterator[str]:
        return self._iterate()

    async def close(self) -> None:
        async with self._close_lock:
            if self._closed:
                return

            self._closed = True
            process = self._process

            if process is not None and process.stdin is not None:
                process.stdin.close()
                try:
                    await process.stdin.wait_closed()
                except (BrokenPipeError, ConnectionResetError):
                    pass

            if process is not None and process.returncode is None:
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=2.0)
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()

            if self._stdout_task is not None:
                await self._stdout_task
            if self._stderr_task is not None:
                await self._stderr_task

    async def _ensure_started(self) -> None:
        if self._process is not None:
            return

        async with self._start_lock:
            if self._process is not None:
                return
            if self._closed:
                raise TransportClosedError("Transport is closed")

            env = None
            if self._env is not None:
                env = os.environ.copy()
                env.update(self._env)

            self._process = await asyncio.create_subprocess_exec(
                self._command,
                *self._args,
                cwd=self._cwd,
                env=env,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            self._stdout_task = asyncio.create_task(self._pump_stdout())
            self._stderr_task = asyncio.create_task(self._pump_stderr())

    async def _iterate(self) -> AsyncIterator[str]:
        await self._ensure_started()

        while True:
            item = await self._queue.get()
            if item is _QUEUE_EOF:
                return
            if isinstance(item, BaseException):
                raise item
            yield str(item)

    async def _pump_stdout(self) -> None:
        process = self._require_process()
        assert process.stdout is not None

        while True:
            line = await process.stdout.readline()
            if not line:
                break
            await self._queue.put(line.decode("utf-8").rstrip("\r\n"))

        returncode = await process.wait()
        if self._closed:
            await self._queue.put(_QUEUE_EOF)
            return

        await self._queue.put(
            ProtocolStreamError(self._format_process_exit_message(returncode))
        )

    async def _pump_stderr(self) -> None:
        process = self._require_process()
        assert process.stderr is not None

        while True:
            line = await process.stderr.readline()
            if not line:
                return
            self._stderr_tail.append(line.decode("utf-8", errors="replace").rstrip())

    def _format_process_exit_message(self, returncode: int) -> str:
        message = f"Transport process exited unexpectedly with code {returncode}"
        if self._stderr_tail:
            message = f"{message}. stderr tail:\n" + "\n".join(self._stderr_tail)
        return message

    def _require_process(self) -> asyncio.subprocess.Process:
        if self._process is None:
            raise TransportClosedError("Transport process has not been started")
        return self._process
