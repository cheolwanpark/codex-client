"""Codex authentication helpers mirroring the CLI's auth.json handling."""
from __future__ import annotations

import asyncio
import base64
import binascii
import json
import os
import queue
import re
import subprocess
import threading
import time
import zlib
from pathlib import Path
from typing import IO, Optional, Callable


class CodexAuthError(RuntimeError):
    """Base exception raised for Codex authentication helper errors."""


class LoginSession:
    """Track an in-flight `codex login` subprocess and its state."""

    _URL_PATTERN = re.compile(r"https://auth\.openai\.com/oauth/authorize[^\s]*")
    _SUCCESS_TOKEN = "Successfully logged in"

    def __init__(
        self,
        process: subprocess.Popen[str],
        on_exit: Optional[Callable[[], None]] = None,
    ) -> None:
        self.process = process
        self.url: Optional[str] = None
        self.success: bool = False
        self.returncode: Optional[int] = None

        self._queue: queue.Queue[tuple[str, str]] = queue.Queue()
        self._stdout_thread = self._spawn_reader(process.stdout, "stdout")
        self._stderr_thread = self._spawn_reader(process.stderr, "stderr")
        self._on_exit = on_exit

    def _spawn_reader(self, stream: Optional[IO[str]], source: str) -> Optional[threading.Thread]:
        if stream is None:
            return None

        def _reader() -> None:
            for line in iter(stream.readline, ""):
                self._queue.put((source, line.rstrip("\r\n")))
            try:
                stream.close()
            except OSError:
                pass

        thread = threading.Thread(target=_reader, name=f"codex-login-{source}", daemon=True)
        thread.start()
        return thread

    def _process_line(self, line: str) -> None:
        if not self.url:
            match = self._URL_PATTERN.search(line)
            if match:
                self.url = match.group(0)
        if self._SUCCESS_TOKEN in line:
            self.success = True

    def _drain_queue(self, timeout: Optional[float]) -> None:
        deadline = None if timeout is None else time.monotonic() + timeout
        first = True
        while True:
            block = first or timeout is None
            first = False
            remaining = None
            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
            try:
                _, line = self._queue.get(block=block, timeout=remaining if block else 0)
            except queue.Empty:
                break
            self._process_line(line)

    def ensure_url(self, attempts: int = 10, interval: float = 0.5) -> str:
        """Ensure the authorization URL has been captured, retrying if needed."""

        for _ in range(attempts):
            self._drain_queue(interval)
            if self.url:
                return self.url
            if self.process.poll() is not None:
                break

        self._drain_queue(0)
        if self.url:
            return self.url
        raise CodexAuthError("codex login did not provide an authorization URL")

    def wait(self, poll_interval: float = 0.5) -> bool:
        """Block until the subprocess exits, returning True on success output."""

        try:
            while self.process.poll() is None:
                self._drain_queue(poll_interval)
        finally:
            self._drain_queue(0)
            self.returncode = self.process.returncode
            if self._on_exit is not None:
                try:
                    self._on_exit()
                finally:
                    self._on_exit = None
        return self.success

    async def wait_async(self) -> bool:
        """Asynchronous counterpart to `wait`, suitable for `await session`."""

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.wait)

    def __await__(self):  # pragma: no cover - thin delegation to async helper
        return self.wait_async().__await__()


class CodexAuth:
    """Helper for working with Codex CLI authentication state."""

    def __init__(self, codex_command: str = "codex") -> None:
        self._codex_command = codex_command
        self._login_process: Optional[subprocess.Popen[str]] = None
        self._process_lock = threading.Lock()

    def is_authenticated(self) -> bool:
        """Return True when auth.json exists and contains usable credentials."""
        try:
            auth = self._read_auth_json()
        except (FileNotFoundError, CodexAuthError):
            return False

        api_key = auth.get("OPENAI_API_KEY")
        if isinstance(api_key, str) and api_key.strip():
            return True

        tokens = auth.get("tokens")
        if isinstance(tokens, dict):
            access = tokens.get("access_token")
            refresh = tokens.get("refresh_token")
            if all(isinstance(value, str) and value.strip() for value in (access, refresh)):
                return True

        return False

    def login(self) -> LoginSession:
        """Start `codex login` and return a session object tracking its progress."""
        with self._process_lock:
            if self._login_process and self._login_process.poll() is None:
                raise CodexAuthError("codex login is already running")
            
            process = subprocess.Popen(
                [self._codex_command, "login"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            self._login_process = process

        def _clear_login_process() -> None:
            with self._process_lock:
                if self._login_process is process:
                    self._login_process = None

        session = LoginSession(process, on_exit=_clear_login_process)
        try:
            session.ensure_url()
        except Exception:
            self._terminate_process(process)
            with self._process_lock:
                self._login_process = None
            raise

        return session

    def logout(self) -> None:
        """Invoke `codex logout` and terminate any background login process."""
        with self._process_lock:
            process = self._login_process
            self._login_process = None

        if process and process.poll() is None:
            self._terminate_process(process)

        result = subprocess.run(
            [self._codex_command, "logout"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode not in (0, 1):
            raise CodexAuthError(
                f"codex logout failed with exit code {result.returncode}: {result.stderr.strip()}"
            )

    def read(self) -> str:
        """Return auth.json encoded as compressed, URL-safe base64 JSON."""
        auth = self._read_auth_json()
        return self._encode_auth_payload(auth)

    def set(self, oauth: str) -> None:
        """Persist the given auth.json payload (compressed base64 or JSON)."""
        payload = self._decode_oauth_payload(oauth)
        auth_file = self._auth_file_path()
        auth_file.parent.mkdir(parents=True, exist_ok=True)

        serialized = json.dumps(payload, indent=2)
        auth_file.write_text(serialized, encoding="utf-8")

        if os.name == "posix":
            os.chmod(auth_file, 0o600)

    def _terminate_process(self, process: subprocess.Popen[str]) -> None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        finally:
            for stream in (process.stdout, process.stderr):
                if stream is not None:
                    try:
                        stream.close()
                    except OSError:
                        pass

    def _read_auth_json(self) -> dict:
        auth_file = self._auth_file_path()
        try:
            raw = auth_file.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise
        except OSError as exc:
            raise CodexAuthError(f"unable to read auth.json: {exc}") from exc

        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise CodexAuthError(f"invalid auth.json contents: {exc}") from exc

    def _auth_file_path(self) -> Path:
        return self._resolve_codex_home() / "auth.json"

    def _resolve_codex_home(self) -> Path:
        env_home = os.environ.get("CODEX_HOME")
        if env_home and env_home.strip():
            path = Path(env_home.strip())
            try:
                return path.resolve(strict=True)
            except FileNotFoundError as exc:
                raise CodexAuthError(
                    f"CODEX_HOME points to a non-existent path: {path}"
                ) from exc

        try:
            home = Path.home()
        except (RuntimeError, OSError) as exc:
            raise CodexAuthError("unable to determine user home directory") from exc
        return home / ".codex"

    def _decode_oauth_payload(self, oauth: str) -> dict:
        trimmed = oauth.strip()
        if not trimmed:
            raise CodexAuthError("empty auth payload provided")

        # Preferred format: urlsafe base64 of zlib-compressed JSON
        try:
            compressed = base64.urlsafe_b64decode(trimmed.encode("ascii"))
            data = zlib.decompress(compressed)
            return json.loads(data.decode("utf-8"))
        except (ValueError, binascii.Error, zlib.error, UnicodeDecodeError, json.JSONDecodeError):
            pass

        # Backward compatibility: plain base64 of JSON
        try:
            decoded_bytes = base64.b64decode(trimmed, validate=True)
            return json.loads(decoded_bytes.decode("utf-8"))
        except (ValueError, binascii.Error, UnicodeDecodeError, json.JSONDecodeError):
            pass

        try:
            return json.loads(trimmed)
        except json.JSONDecodeError as exc:
            raise CodexAuthError("oauth payload must decode to valid JSON") from exc

    def _encode_auth_payload(self, payload: dict) -> str:
        data = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        compressed = zlib.compress(data, level=9)
        return base64.urlsafe_b64encode(compressed).decode("ascii")
