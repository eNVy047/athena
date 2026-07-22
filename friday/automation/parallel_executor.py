from __future__ import annotations

import asyncio
from typing import List, Callable, Coroutine, Any

class ParallelExecutor:
    async def execute_parallel(self, tasks: List[Callable[[], Coroutine[Any, Any, Any]]]) -> List[Any]:
        """Runs multiple async execution tasks concurrently."""
        if not tasks:
            return []
        # Gather all tasks concurrently
        return await asyncio.gather(*[task() for task in tasks], return_exceptions=True)
