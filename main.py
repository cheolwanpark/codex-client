#!/usr/bin/env python3
"""
Test script for codex_sdk library.

This script demonstrates the usage pattern:
- Takes user input
- Shows streaming response
- Gets final message
"""

import asyncio
import sys
from src.codex_sdk import *


async def main():
    print("🚀 Codex SDK Test")
    print("=" * 40)

    # Get user input
    try:
        prompt = input("Enter your prompt: ").strip()
        if not prompt:
            prompt = "Hey! Introduce yourself."
            print(f"Using default prompt: {prompt}")
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
        return

    print(f"\n💬 Prompt: {prompt}")
    print("-" * 40)

    try:
        async with Session() as session:
            print("✅ Connected to Codex")

            print("📝 Streaming response:")
            config = {
                "mcp_servers.context7": {
                    "args": [
                        "-y",
                        "@upstash/context7-mcp",
                        "--api-key",
                        "ctx7sk-93e85b8b-f1c1-47b9-886a-0be32c255f1f"
                    ],
                    "command": "npx"
                }
            }
            i = 0
            async for message in session.chat(prompt, config=config):
                i += 1
                print(f"Message {i}")
                async for part in message:
                    # Agent Message: Delta event -> ... -> Message event
                    if isinstance(part, AgentMessageDeltaEvent):
                        print(part.delta, end='', flush=True)
                    elif isinstance(part, AgentMessageEvent):
                        print("\nMessage complete.")

                    # Reasoning: Section break event -> Reasoning delta event -> ... -> Reasoning event
                    elif isinstance(part, AgentReasoningSectionBreakEvent):
                        print(f"🤔 Reasoning: ", end='')
                    elif isinstance(part, AgentReasoningDeltaEvent):
                        print(part.delta, end='', flush=True)
                    elif isinstance(part, AgentReasoningEvent):
                        print("\nReasoning complete.")

                    # MCP Tool Call: Begin event -> End event
                    elif isinstance(part, McpToolCallBeginEvent):
                        print(f"\n🔧 Tool Call: {part.invocation.server}.{part.invocation.tool}(", end='')
                        print(", ".join(f"{k}={v}" for k, v in part.invocation.arguments.items()), end=')\n')
                    elif isinstance(part, McpToolCallEndEvent):
                        print(f"\n🔧 Tool Call End: {part.invocation.tool}, Duration: {part.duration.secs}s")

                print()
                msg = await message.get()
                print(f"📋 Message length: {len(msg)} characters")

            print("\n")
            print("-" * 40)

            print("✅ Test completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
        sys.exit(0)
