import asyncio
import logging

logger = logging.getLogger(__name__)

class TimeoutManager:
    """Enforces strict timeouts on asynchronous operations."""
    
    @staticmethod
    async def run_with_timeout(timeout_seconds: float, coro, *args, **kwargs):
        try:
            return await asyncio.wait_for(coro(*args, **kwargs), timeout=timeout_seconds)
        except asyncio.TimeoutError:
            logger.error(f"Operation timed out after {timeout_seconds}s.")
            raise
