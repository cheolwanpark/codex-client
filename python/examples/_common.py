from __future__ import annotations

import shutil

from codex_harness_kit import client_info

CLIENT_INFO = client_info("codex-harness-kit-examples", "0.1.0")


def require_codex_cli() -> None:
    if shutil.which("codex") is None:
        raise SystemExit(
            "The `codex` CLI was not found on PATH. Install it and authenticate before running examples."
        )


def print_section(title: str) -> None:
    print(f"\n== {title} ==")
