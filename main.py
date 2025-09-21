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
from src.codex_sdk import Session


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
            i = 0
            last_message = None
            async for message in session.chat(prompt):
                i += 1
                print(f"Message {i}")
                async for part in message:
                    print(part, end='', flush=True)
                print()
                last_message = message

            print("\n")
            print("-" * 40)

            # Get final message (should work after streaming)
            if last_message:
                final = await last_message.get()
                print(f"📋 Final message length: {len(final)} characters")
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
