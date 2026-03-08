from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator


async def next_message(iterator: AsyncIterator[object], timeout: float = 10.0) -> object:
    return await asyncio.wait_for(anext(iterator), timeout=timeout)
