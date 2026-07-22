import asyncio
from typing import Tuple, Any

class PriorityTaskQueue:
    def __init__(self):
        self._queue = asyncio.PriorityQueue()

    async def enqueue(self, priority: int, task_item: Any) -> None:
        """Enqueues a task item with priority (lower int executes first)."""
        await self._queue.put((priority, task_item))

    async def dequeue(self) -> Tuple[int, Any]:
        """Dequeues the highest priority task item."""
        return await self._queue.get()

    def task_done(self) -> None:
        self._queue.task_done()
        
    def empty(self) -> bool:
        return self._queue.empty()
