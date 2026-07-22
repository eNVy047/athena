import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)

class RetryManager:
    """Manages retry limits and backoff wait times for tasks."""
    def __init__(self, default_max_retries: int = 3, default_backoff: float = 1.0):
        self.default_max_retries = default_max_retries
        self.default_backoff = default_backoff

    async def execute_with_retry(self, action_func: Any, params: Any, max_retries: int = None, backoff: float = None) -> Any:
        retries = max_retries if max_retries is not None else self.default_max_retries
        wait = backoff if backoff is not None else self.default_backoff
        
        attempt = 0
        while attempt <= retries:
            try:
                return await action_func(params)
            except Exception as e:
                attempt += 1
                if attempt > retries:
                    raise e
                logger.warning(f"Action failed: {e}. Retrying in {wait}s... (Attempt {attempt}/{retries})")
                await asyncio.sleep(wait)
                wait *= 2
