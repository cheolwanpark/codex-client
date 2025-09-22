"""Custom exceptions for the Codex SDK."""


class CodexError(Exception):
    """Base exception for all Codex SDK errors."""
    pass


class ConnectionError(CodexError):
    """Raised when there's an issue connecting to the Codex MCP server."""
    pass


class ChatError(CodexError):
    """Raised when there's an issue with chat handling or retrieval."""
    pass


class ToolError(CodexError):
    """Raised when a tool call fails."""
    pass
