from __future__ import annotations

import json
from pathlib import Path

from codex_harness_kit._generated import (
    CLIENT_REQUEST_METHODS,
    SERVER_NOTIFICATION_METHODS,
    SERVER_REQUEST_METHODS,
)


def test_generated_method_registries_match_schema_unions() -> None:
    assert set(CLIENT_REQUEST_METHODS) == _extract_methods(_repo_root() / "schema/ClientRequest.json")
    assert set(SERVER_REQUEST_METHODS) == _extract_methods(_repo_root() / "schema/ServerRequest.json")
    assert set(SERVER_NOTIFICATION_METHODS) == _extract_methods(
        _repo_root() / "schema/ServerNotification.json"
    )


def _extract_methods(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        variant["properties"]["method"]["enum"][0]
        for variant in data["oneOf"]
    }


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]
