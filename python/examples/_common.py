from __future__ import annotations

import shutil

CLIENT_INFO = {"name": "codex-harness-kit-examples", "version": "0.1.0"}


def require_codex_cli() -> None:
    if shutil.which("codex") is None:
        raise SystemExit(
            "The `codex` CLI was not found on PATH. Install it and authenticate before running examples."
        )


def print_section(title: str) -> None:
    print(f"\n== {title} ==")
