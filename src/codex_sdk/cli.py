"""Command-line interface for Codex SDK authentication helpers."""
from __future__ import annotations

import argparse
import sys
from typing import TextIO

from .auth import CodexAuth, CodexAuthError


class _Console:
    """Lightweight console helper for consistent, styled output."""

    _RESET = "\033[0m"
    _COLORS = {
        "title": "\033[95m",
        "info": "\033[36m",
        "success": "\033[32m",
        "warning": "\033[33m",
        "error": "\033[31m",
    }
    _PREFIXES = {
        "info": "[INFO]",
        "success": "[ OK ]",
        "warning": "[WARN]",
        "error": "[FAIL]",
    }

    def __init__(self, stream: TextIO, width: int = 64) -> None:
        self.stream = stream
        self.width = width
        self._interactive = bool(getattr(stream, "isatty", lambda: False)())
        self._use_color = self._interactive

    def _write(self, message: str = "") -> None:
        print(message, file=self.stream)

    def _stylize(self, kind: str, message: str) -> str:
        prefix = self._PREFIXES.get(kind, "[INFO]")
        if not self._use_color:
            return f"{prefix} {message}"
        color = self._COLORS.get(kind, self._COLORS["info"])
        return f"{color}{prefix}{self._RESET} {message}"

    def headline(self, title: str) -> None:
        if not self._interactive:
            self._write(title)
            self._write("-" * len(title))
            return
        line = "=" * min(self.width, max(len(title) + 4, 20))
        color = self._COLORS["title"] if self._use_color else ""
        reset = self._RESET if self._use_color else ""
        self._write(line)
        self._write(f" {color}{title}{reset}")
        self._write(line)

    def status(self, kind: str, message: str) -> None:
        self._write(self._stylize(kind, message))

    def section(self, label: str) -> None:
        if not self._interactive:
            self._write(f"{label}:")
            return
        self._write(f"-- {label} --")

    def block(self, text: str) -> None:
        for line in text.splitlines() or [""]:
            self._write(f"    {line}")

    def guidance(self, steps: list[str]) -> None:
        if not steps:
            return
        self._write("Next steps:")
        for idx, step in enumerate(steps, start=1):
            self._write(f"  {idx}. {step}")

    def blank(self) -> None:
        self._write()

    @property
    def interactive(self) -> bool:
        return self._interactive


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Codex SDK authentication helper")
    subparsers = parser.add_subparsers(dest="command")

    login_parser = subparsers.add_parser("login", help="Start login flow and show URL")

    subparsers.add_parser("logout", help="Clear stored authentication state")
    subparsers.add_parser("read", help="Print auth.json content (base64 encoded)")

    set_parser = subparsers.add_parser("set", help="Write auth.json content from base64 payload")
    set_parser.add_argument("payload", help="Base64-encoded auth.json payload")

    return parser


def _cmd_login(auth: CodexAuth) -> int:
    console = _Console(sys.stdout)
    err_console = _Console(sys.stderr)

    try:
        session = auth.login()
    except CodexAuthError as exc:
        err_console.status("error", f"Login failed: {exc}")
        return 1

    url = session.url
    if url is None:
        err_console.status("error", "codex-client did not return an authorization URL.")
        return 1

    if not console.interactive:
        print(url)
        try:
            success = session.wait()
        except KeyboardInterrupt:
            err_console.status("warning", "Login interrupted by user.")
            return 1
        if success:
            err_console.status("success", "codex-client reported successful login.")
            return 0
        code = session.returncode
        if code not in (0, None):
            err_console.status("error", f"codex-client login exited with code {code}.")
        else:
            err_console.status("warning", "codex-client exited before confirming login.")
        return 1

    console.headline("Codex Login")
    console.status("success", "Authorization URL generated.")
    console.blank()
    console.section("Authorization URL")
    console.block(url)
    console.blank()

    console.status(
        "info",
        "codex-client is opening your browser automatically.",
    )
    console.guidance([
        "Check for a new browser tab from Codex if it is not already frontmost.",
        "Sign in and approve the authorization request.",
        "If no tab appears, copy the URL above into any browser and complete the flow.",
    ])

    console.blank()
    console.status("info", "Waiting for codex-client to confirm login (Ctrl+C to cancel)...")
    try:
        success = session.wait()
    except KeyboardInterrupt:
        console.blank()
        err_console.status("warning", "Login interrupted before completion.")
        return 1

    if success:
        console.status("success", "codex-client reported successful login.")
        return 0

    code = session.returncode
    if code not in (0, None):
        err_console.status("error", f"codex-client login exited with code {code}.")
    else:
        err_console.status("warning", "codex-client exited before confirming login.")
    return 1


def _cmd_logout(auth: CodexAuth) -> int:
    console = _Console(sys.stdout)
    err_console = _Console(sys.stderr)

    try:
        auth.logout()
    except CodexAuthError as exc:
        err_console.status("error", f"Logout failed: {exc}")
        return 1

    if not console.interactive:
        print("Logged out")
        return 0

    console.headline("Codex Logout")
    console.status("success", "Local credentials removed.")
    console.guidance([
        "Run `codex-client login` when you need to authenticate again.",
        "Delete any copied auth payloads you no longer need.",
    ])
    return 0


def _cmd_read(auth: CodexAuth) -> int:
    console = _Console(sys.stdout)
    err_console = _Console(sys.stderr)

    try:
        payload = auth.read()
    except CodexAuthError as exc:
        err_console.status("error", f"Read failed: {exc}")
        return 1
    except FileNotFoundError:
        err_console.status("error", "auth.json not found")
        return 1

    if not console.interactive:
        print(payload)
        return 0

    console.headline("Stored Codex Credentials")
    console.status(
        "info",
        "Retrieved compressed URL-safe base64 payload from auth.json.",
    )
    console.blank()
    console.section("Payload")
    console.block(payload)
    console.blank()
    console.guidance([
        "Keep this payload secret; it grants access to your Codex account.",
        "Use `codex-client set <payload>` on another machine to import it.",
        "Run `codex-client logout` to clear credentials when finished.",
    ])
    console.blank()
    console.section("Use in Python")
    console.block(
        "from codex_sdk.auth import CodexAuth\n"
        "auth = CodexAuth(codex_command=\"codex-client\")\n"
        "auth.set(\"<payload>\")  # paste the string above\n"
    )
    return 0


def _cmd_set(auth: CodexAuth, payload: str) -> int:
    console = _Console(sys.stdout)
    err_console = _Console(sys.stderr)

    try:
        auth.set(payload)
    except CodexAuthError as exc:
        err_console.status("error", f"Set failed: {exc}")
        return 1

    if not console.interactive:
        print("auth.json updated")
        return 0

    console.headline("Credentials Updated")
    console.status("success", "auth.json now contains the provided payload.")
    console.guidance([
        "Verify the stored value with `codex-client read`.",
        "Keep the payload source in a secure location or delete it.",
    ])
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    auth = CodexAuth()

    if args.command == "login":
        return _cmd_login(auth)
    if args.command == "logout":
        return _cmd_logout(auth)
    if args.command == "read":
        return _cmd_read(auth)
    if args.command == "set":
        return _cmd_set(auth, payload=args.payload)

    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
