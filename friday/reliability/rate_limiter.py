import time
import asyncio

class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        
    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        if new_tokens > 0:
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.last_refill = now
            
    async def acquire(self, amount: int = 1):
        while True:
            self._refill()
            if self.tokens >= amount:
                self.tokens -= amount
                return
            
            # Wait a bit before trying again
            wait_time = (amount - self.tokens) / self.refill_rate
            if wait_time > 0:
                await asyncio.sleep(wait_time)
