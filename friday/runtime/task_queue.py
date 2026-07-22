import asyncio
from typing import Dict, Any, List, Optional
from friday.core.cognition.models import Task

class TaskQueue:
    """Multi-strategy queue supporting Priority ordering and Task dependencies."""
    def __init__(self):
        self._queue: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()

    async def enqueue(self, task: Task, priority: int = 0) -> None:
        async with self._lock:
            # Insert sorting by priority desc
            self._queue.append({"task": task, "priority": priority})
            self._queue.sort(key=lambda x: x["priority"], reverse=True)

    async def dequeue(self) -> Optional[Task]:
        async with self._lock:
            if not self._queue:
                return None
            item = self._queue.pop(0)
            return item["task"]

    async def is_empty(self) -> bool:
        async with self._lock:
            return len(self._queue) == 0

    async def size(self) -> int:
        async with self._lock:
            return len(self._queue)
