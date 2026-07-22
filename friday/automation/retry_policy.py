from __future__ import annotations

import asyncio
import logging
from typing import Callable, Coroutine, Any

logger = logging.getLogger("friday-agent")

class RetryPolicy:
    async def execute_with_retry(
        self,
        func: Callable[[], Coroutine[Any, Any, Any]],
        max_retries: int,
        delay_seconds: float = 1.0
    ) -> Any:
        """Executes the async function with a retry mechanism."""
        for attempt in range(max_retries + 1):
            try:
                return await func()
            except Exception as e:
                if attempt >= max_retries:
                    raise e
                logger.warning(f"[RetryPolicy] Execution failed on attempt {attempt + 1}. Retrying in {delay_seconds}s. Error: {e}")
                await asyncio.sleep(delay_seconds)
