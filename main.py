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
    McpToolCallBeginEvent, McpToolCallEndEvent,
    SessionConfiguredEvent, TaskCompleteEvent, TaskStartedEvent,
    TokenCountEvent
)
from src.codex_sdk.structured import (
    AssistantMessageStream,
    CommandStream,
    ReasoningStream,
    structured
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
            config = CodexChatConfig(
                profile=CodexProfile(
                    model="gpt-5",
                    reasoning_effort=ReasoningEffort.MINIMAL,
                    verbosity=Verbosity.HIGH,
                    sandbox=SandboxMode.DANGER_FULL_ACCESS,
                ),
                mcp_servers=[
                    CodexMcpServer(
                        name="context7",
                        command="npx",
                        args=[
                            "-y",
                            "@upstash/context7-mcp",
                            "--api-key",
                            "ctx7sk-93e85b8b-f1c1-47b9-886a-0be32c255f1f",
                        ],
                    )
                ]
            )
            chat = await client.create_chat(prompt, config=config)
            
            turn = 1

            while True:
                print(f"🔄 Turn {turn}")
                async for event in structured(chat):
                    # Aggregated assistant response stream
                    if isinstance(event, AssistantMessageStream):
                        async for chunk in event.stream():
                            print(chunk, end='', flush=True)
                        print("\nMessage complete.")
                        continue

                    # Aggregated reasoning stream
                    if isinstance(event, ReasoningStream):
                        print("🤔 Reasoning: ", end='')
                        async for chunk in event.stream():
                            print(chunk, end='', flush=True)
                        print("\nReasoning complete.")
                        continue

                    # Aggregated command execution stream
                    if isinstance(event, CommandStream):
                        cmd_str = ' '.join(event.command)
                        print(f"\n⚡ Executing: {cmd_str}")
                        async for chunk in event.stream():
                            if chunk.text is not None:
                                print(chunk.text, end='', flush=True)
                            else:
                                print(f"[binary: {len(chunk.data)} bytes]", end='', flush=True)
                        if event.exit_code is not None:
                            duration = event.duration.total_seconds() if event.duration else None
                            status = "✅" if event.exit_code == 0 else "❌"
                            summary = f"{status} Command exited {event.exit_code}"
                            if duration is not None:
                                summary += f" in {duration:.3f}s"
                            print(f"\n{summary}")
                        continue

                    # Session/Task Lifecycle
                    if isinstance(event, SessionConfiguredEvent):
                        print(f"\n🔧 Session configured: {event.model}")
                        if event.reasoning_effort:
                            print(f"   Reasoning effort: {event.reasoning_effort.value}")
                        continue
                    if isinstance(event, TaskStartedEvent):
                        if event.model_context_window:
                            print(f"\n🚀 Task started (context: {event.model_context_window:,} tokens)")
                        else:
                            print(f"\n🚀 Task started")
                        continue
                    if isinstance(event, TaskCompleteEvent):
                        print(f"\n🎉 Task complete")
                        if event.last_agent_message:
                            print(f"   Final message: {event.last_agent_message[:100]}...")
                        continue

                    # Token Usage
                    if isinstance(event, TokenCountEvent):
                        if event.info:
                            total = event.info.total_token_usage.total_tokens
                            last = event.info.last_token_usage.total_tokens
                            print(f"\n💰 Tokens: {total:,} total, +{last:,} this turn")
                        continue

                    # MCP Tool Call: Begin event -> End event
                    if isinstance(event, McpToolCallBeginEvent):
                        print(f"\n🔧 Tool Call: {event.invocation.server}.{event.invocation.tool}(", end='')
                        if event.invocation.arguments:
                            print(", ".join(f"{k}={v}" for k, v in event.invocation.arguments.items()), end=')\n')
                        else:
                            print(')\n', end='')
                        continue
                    if isinstance(event, McpToolCallEndEvent):
                        duration = event.duration.total_seconds()
                        print(f"\n🔧 Tool Call End: {event.invocation.tool}, Duration: {duration:.3f}s")
                        if hasattr(event.result, 'Ok'):
                            print(f"   ✅ Success: {len(event.result.Ok.content)} content block(s)")
                        elif hasattr(event.result, 'Err'):
                            print(f"   ❌ Error: {event.result.Err}")
                        continue

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
