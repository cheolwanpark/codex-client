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
        async with Client() as client:
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
            chat = await client.create_chat(prompt, config=config)
            
            turn = 1

            while True:
                print(f"🔄 Turn {turn}")
                async for event in chat:
                    # Agent Message: Delta event -> ... -> Message event
                    if isinstance(event, AgentMessageDeltaEvent):
                        print(event.delta, end='', flush=True)
                    elif isinstance(event, AgentMessageEvent):
                        print("\nMessage complete.")

                    # Reasoning: Section break event -> Reasoning delta event -> ... -> Reasoning event
                    elif isinstance(event, AgentReasoningSectionBreakEvent):
                        print(f"🤔 Reasoning: ", end='')
                    elif isinstance(event, AgentReasoningDeltaEvent):
                        print(event.delta, end='', flush=True)
                    elif isinstance(event, AgentReasoningEvent):
                        print("\nReasoning complete.")

                    # Command Execution: Begin -> Output Delta -> End
                    elif isinstance(event, ExecCommandBeginEvent):
                        cmd_str = ' '.join(event.command)
                        print(f"\n⚡ Executing: {cmd_str}")
                    elif isinstance(event, ExecCommandOutputDeltaEvent):
                        try:
                            output = event.decoded_text
                            print(output, end='', flush=True)
                        except UnicodeDecodeError:
                            print(f"[binary: {len(event.decoded_chunk)} bytes]", end='', flush=True)
                    elif isinstance(event, ExecCommandEndEvent):
                        duration = event.duration.total_seconds()
                        if event.exit_code == 0:
                            print(f"\n✅ Command completed in {duration:.3f}s")
                        else:
                            print(f"\n❌ Command failed (exit {event.exit_code}) in {duration:.3f}s")

                    # Session/Task Lifecycle
                    elif isinstance(event, SessionConfiguredEvent):
                        print(f"\n🔧 Session configured: {event.model}")
                        if event.reasoning_effort:
                            print(f"   Reasoning effort: {event.reasoning_effort.value}")
                    elif isinstance(event, TaskStartedEvent):
                        if event.model_context_window:
                            print(f"\n🚀 Task started (context: {event.model_context_window:,} tokens)")
                        else:
                            print(f"\n🚀 Task started")
                    elif isinstance(event, TaskCompleteEvent):
                        print(f"\n🎉 Task complete")
                        if event.last_agent_message:
                            print(f"   Final message: {event.last_agent_message[:100]}...")

                    # Token Usage
                    elif isinstance(event, TokenCountEvent):
                        if event.info:
                            total = event.info.total_token_usage.total_tokens
                            last = event.info.last_token_usage.total_tokens
                            print(f"\n💰 Tokens: {total:,} total, +{last:,} this turn")

                    # MCP Tool Call: Begin event -> End event
                    elif isinstance(event, McpToolCallBeginEvent):
                        print(f"\n🔧 Tool Call: {event.invocation.server}.{event.invocation.tool}(", end='')
                        if event.invocation.arguments:
                            print(", ".join(f"{k}={v}" for k, v in event.invocation.arguments.items()), end=')\n')
                        else:
                            print(')\n', end='')
                    elif isinstance(event, McpToolCallEndEvent):
                        duration = event.duration.total_seconds()
                        print(f"\n🔧 Tool Call End: {event.invocation.tool}, Duration: {duration:.3f}s")
                        # Handle Rust Result wrapper
                        if hasattr(event.result, 'Ok'):
                            print(f"   ✅ Success: {len(event.result.Ok.content)} content block(s)")
                        elif hasattr(event.result, 'Err'):
                            print(f"   ❌ Error: {event.result.Err}")

                print()
                msg = await chat.get()
                print(f"📋 Message length: {len(msg)} characters")

                print("\n")
                print("-" * 40)

                prompt = input("Enter your next prompt (or leave empty to quit): ").strip()
                if not prompt:
                    print("👋 Goodbye!")
                    break
                await chat.resume(prompt)
                turn += 1

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
