"""Utilities for parsing Codex MCP events from log messages."""

from __future__ import annotations

import ast
import json
import re
from typing import Any, Dict, Optional

from ..event import CodexEventMsg, parse_event

_PARAMS_PATTERN = re.compile(r"params=(\{.*?\})\s+jsonrpc=", re.DOTALL)


def extract_event_payload(message: str) -> Optional[Dict[str, Any]]:
    """Extract the raw event payload from an MCP validation warning."""

    match = _PARAMS_PATTERN.search(message)
    if not match:
        return None

    params_fragment = match.group(1)

    for loader in (_load_via_ast, _load_via_json):
        params = loader(params_fragment)
        if isinstance(params, dict):
            msg = params.get("msg")
            meta = params.get("_meta")
            if isinstance(msg, dict) and isinstance(meta, dict):
                event_dict = dict(msg)
                event_dict["_meta"] = meta
                return event_dict

    return None


def parse_event_from_message(message: str) -> Optional[CodexEventMsg]:
    """Parse a typed Codex event from a log message, if possible."""

    payload = extract_event_payload(message)
    if payload is None:
        return None

    try:
        return parse_event(payload)
    except Exception:
        return None


def _load_via_ast(fragment: str) -> Optional[Dict[str, Any]]:
    try:
        return ast.literal_eval(fragment)
    except (SyntaxError, ValueError):
        return None


def _load_via_json(fragment: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(fragment)
    except json.JSONDecodeError:
        return None


__all__ = [
    "extract_event_payload",
    "parse_event_from_message",
]
