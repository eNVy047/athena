import time
import logging
from typing import Callable, Any, Awaitable

logger = logging.getLogger(__name__)

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    """Prevents cascading failures when a downstream dependency is failing."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.failures = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
    def record_success(self):
        self.failures = 0
        self.state = "CLOSED"
        
    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning("Circuit breaker OPENED due to multiple failures.")
            
    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        # HALF_OPEN
        return True
        
    async def call(self, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        if not self.can_execute():
            raise CircuitBreakerOpenException("Circuit breaker is OPEN.")
            
        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise e
