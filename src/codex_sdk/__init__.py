"""
Codex SDK - A minimal library for programmatic control of Codex.

Usage:
    from codex_sdk import Session

    async with Session() as session:
        # Single message usage
        async for message in session.chat("Hello, Codex!"):
            # Stream the response
            async for part in message:
                print(part, end='', flush=True)

            # Or get the complete response
            response = await message.get()
            print(response)

        # Multiple messages usage
        async for i, message in enumerate(session.chat("Tell me a story in two parts")):
            print(f"Message {i+1}")
            async for part in message:
                print(part, end='', flush=True)
            print()
"""

from .session import Session
from .message import Message
from .exceptions import CodexError, ConnectionError, MessageError, ToolError

__version__ = "0.1.0"

__all__ = [
    "Session",
    "Message",
    "CodexError",
    "ConnectionError",
    "MessageError",
    "ToolError",
]