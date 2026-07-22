import asyncio
import logging
from typing import Callable, Any, Awaitable, Type, Tuple

logger = logging.getLogger(__name__)

class RetryManager:
    """Standardized retry logic with backoff for transient failures."""
    
    @staticmethod
    async def with_retry(
        func: Callable[..., Awaitable[Any]],
        *args,
        max_retries: int = 3,
        initial_backoff: float = 1.0,
        backoff_factor: float = 2.0,
        exceptions: Tuple[Type[Exception], ...] = (Exception,),
        **kwargs
    ) -> Any:
        
        retries = 0
        backoff = initial_backoff
        
        while True:
            try:
                return await func(*args, **kwargs)
            except exceptions as e:
                retries += 1
                if retries > max_retries:
                    logger.error(f"Max retries ({max_retries}) exceeded for {func.__name__}. Last error: {e}")
                    raise e
                
                logger.warning(f"Retry {retries}/{max_retries} for {func.__name__} after {backoff}s. Error: {e}")
                await asyncio.sleep(backoff)
                backoff *= backoff_factor
