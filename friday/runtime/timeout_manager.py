import asyncio
from typing import Any

class TimeoutManager:
    """Safely executes tasks within a configured timeout window."""
    def __init__(self, default_timeout: float = 30.0):
        self.default_timeout = default_timeout

    async def execute_with_timeout(self, action_func: Any, params: Any, timeout: float = None) -> Any:
        limit = timeout if timeout is not None else self.default_timeout
        return await asyncio.wait_for(action_func(params), timeout=limit)
