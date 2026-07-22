import asyncio
from typing import Set

class BackgroundTaskManager:
    def __init__(self):
        self._tasks: Set[asyncio.Task] = set()

    def submit(self, coro) -> asyncio.Task:
        task = asyncio.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    async def shutdown(self, timeout: float = 5.0):
        if not self._tasks:
            return
        
        for task in self._tasks:
            task.cancel()
            
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
