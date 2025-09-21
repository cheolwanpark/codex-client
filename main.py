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
from src.codex_sdk.event import (
    AgentMessageEvent, AgentMessageDeltaEvent,
    AgentReasoningEvent, AgentReasoningDeltaEvent, AgentReasoningSectionBreakEvent,
    ExecCommandBeginEvent, ExecCommandEndEvent, ExecCommandOutputDeltaEvent,
    McpToolCallBeginEvent, McpToolCallEndEvent,
    SessionConfiguredEvent, TaskStartedEvent, TaskCompleteEvent,
    TokenCountEvent
)


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

                    # Command Execution: Begin -> Output Delta -> End
                    elif isinstance(part, ExecCommandBeginEvent):
                        cmd_str = ' '.join(part.command)
                        print(f"\n⚡ Executing: {cmd_str}")
                    elif isinstance(part, ExecCommandOutputDeltaEvent):
                        try:
                            output = part.decoded_text
                            print(output, end='', flush=True)
                        except UnicodeDecodeError:
                            print(f"[binary: {len(part.decoded_chunk)} bytes]", end='', flush=True)
                    elif isinstance(part, ExecCommandEndEvent):
                        duration = part.duration.total_seconds()
                        if part.exit_code == 0:
                            print(f"\n✅ Command completed in {duration:.3f}s")
                        else:
                            print(f"\n❌ Command failed (exit {part.exit_code}) in {duration:.3f}s")

                    # Session/Task Lifecycle
                    elif isinstance(part, SessionConfiguredEvent):
                        print(f"\n🔧 Session configured: {part.model}")
                        if part.reasoning_effort:
                            print(f"   Reasoning effort: {part.reasoning_effort.value}")
                    elif isinstance(part, TaskStartedEvent):
                        if part.model_context_window:
                            print(f"\n🚀 Task started (context: {part.model_context_window:,} tokens)")
                        else:
                            print(f"\n🚀 Task started")
                    elif isinstance(part, TaskCompleteEvent):
                        print(f"\n🎉 Task complete")
                        if part.last_agent_message:
                            print(f"   Final message: {part.last_agent_message[:100]}...")

                    # Token Usage
                    elif isinstance(part, TokenCountEvent):
                        if part.info:
                            total = part.info.total_token_usage.total_tokens
                            last = part.info.last_token_usage.total_tokens
                            print(f"\n💰 Tokens: {total:,} total, +{last:,} this turn")

                    # MCP Tool Call: Begin event -> End event
                    elif isinstance(part, McpToolCallBeginEvent):
                        print(f"\n🔧 Tool Call: {part.invocation.server}.{part.invocation.tool}(", end='')
                        if part.invocation.arguments:
                            print(", ".join(f"{k}={v}" for k, v in part.invocation.arguments.items()), end=')\n')
                        else:
                            print(')\n', end='')
                    elif isinstance(part, McpToolCallEndEvent):
                        duration = part.duration.total_seconds()
                        print(f"\n🔧 Tool Call End: {part.invocation.tool}, Duration: {duration:.3f}s")
                        # Handle Rust Result wrapper
                        if hasattr(part.result, 'Ok'):
                            print(f"   ✅ Success: {len(part.result.Ok.content)} content block(s)")
                        elif hasattr(part.result, 'Err'):
                            print(f"   ❌ Error: {part.result.Err}")

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
