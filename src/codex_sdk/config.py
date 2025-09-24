"""Configuration models for Codex chat sessions and related tooling."""

from __future__ import annotations

import re
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_serializer


def _snake_case(value: str) -> str:
    """Convert arbitrary strings to a lowercase snake_case representation."""

    if not value:
        return value

    value = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", value)
    value = re.sub("([a-z0-9])([A-Z])", r"\1_\2", value)
    value = re.sub(r"[^0-9a-zA-Z]+", "_", value)
    return value.strip("_").lower()

def random_word(n):
    import string, random
    letters = string.ascii_lowercase  
    return ''.join(random.choice(letters) for _ in range(n))


class ApprovalPolicy(str, Enum):
    """Supported approval policy values for Codex sessions."""

    UNTRUSTED = "untrusted"
    ON_FAILURE = "on-failure"
    ON_REQUEST = "on-request"
    NEVER = "never"


class SandboxMode(str, Enum):
    """Filesystem sandboxing modes available to the Codex runtime."""

    READ_ONLY = "read-only"
    WORKSPACE_WRITE = "workspace-write"
    DANGER_FULL_ACCESS = "danger-full-access"


class ReasoningEffort(str, Enum):
    """Reasoning effort levels supported by Codex profiles."""

    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Verbosity(str, Enum):
    """Verbosity levels for Codex profile responses."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CodexMcpServer(BaseModel):
    """Configuration for an MCP server that Codex can launch."""

    model_config = ConfigDict(extra="forbid")

    name: str
    command: str
    args: Optional[List[str]] = None
    envs: Optional[Dict[str, str]] = None
    setup_timeout_sec: Optional[int] = None
    tool_timeout_sec: Optional[int] = None

    @model_serializer(mode="plain")
    def _serialize(self) -> Dict[str, Dict[str, Any]]:
        """Produce the config block keyed by snake_cased server name."""

        key = f"mcp_servers.{_snake_case(self.name)}"
        payload: Dict[str, Any] = {"command": self.command}
        if self.args is not None:
            payload["args"] = self.args
        if self.envs is not None:
            payload["envs"] = self.envs
        if self.setup_timeout_sec is not None:
            payload["setup_timeout_sec"] = self.setup_timeout_sec
        if self.tool_timeout_sec is not None:
            payload["tool_timeout_sec"] = self.tool_timeout_sec
        return {key: payload}


class CodexProfile(BaseModel):
    """Profile describing how Codex should execute within a session."""

    model_config = ConfigDict(extra="forbid")

    model: str
    name: str = Field(default_factory=lambda: random_word(10))
    reasoning_effort: Optional[ReasoningEffort] = None
    verbosity: Optional[Verbosity] = None
    sandbox: Optional[SandboxMode] = None

    @model_serializer(mode="plain")
    def _serialize(self) -> Dict[str, Any]:
        """Produce the config block keyed by snake_cased server name."""
        
        key = f"profiles.{_snake_case(self.name)}"
        payload: Dict[str, Any] = {
            "model": self.model,
            "model_provider": "openai"
        }
        if self.reasoning_effort is not None:
            payload["model_reasoning_effort"] = self.reasoning_effort
        if self.verbosity is not None:
            payload["model_verbosity"] = self.verbosity
        if self.sandbox is not None:
            payload["sandbox_mode"] = self.sandbox
        return {key: payload}


class CodexChatConfig(BaseModel):
    """Top-level configuration for :func:`Client.create_chat`. All fields optional."""

    model_config = ConfigDict(extra="forbid")

    approval_policy: Optional[ApprovalPolicy] = None
    base_instruction: Optional[str] = None
    cwd: Optional[str] = None
    model: Optional[str] = None
    sandbox: Optional[SandboxMode] = None
    profile: Optional[CodexProfile] = None
    mcp_servers: Optional[List[CodexMcpServer]] = None
    envs: Optional[Dict[str, str]] = None

    @model_serializer(mode="plain")
    def _serialize(self) -> Dict[str, Any]:
        """Produce the config block keyed by snake_cased server name."""
        payload: Dict[str, Any] = {}
        if self.approval_policy is not None:
            payload["approval-policy"] = self.approval_policy
        if self.base_instruction is not None:
            payload["base-instructions"] = self.base_instruction
        if self.cwd is not None:
            payload["cwd"] = self.cwd
        if self.model is not None:
            payload["model"] = self.model
        if self.sandbox is not None:
            payload["sandbox"] = self.sandbox

        config: Dict[str, Any] = {}
        if self.profile is not None:
            config.update(self.profile._serialize())
            payload["profile"] = _snake_case(self.profile.name)
        if self.mcp_servers is not None:
            for server in self.mcp_servers:
                config.update(server._serialize())
        if self.envs is not None:
            config.update({
                "shell_environment_policy": {
                    "set": self.envs
                }
            })
        payload["config"] = config

        return payload


__all__ = [
    "ApprovalPolicy",
    "SandboxMode",
    "ReasoningEffort",
    "Verbosity",
    "CodexMcpServer",
    "CodexProfile",
    "CodexChatConfig",
]
