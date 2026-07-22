import asyncio
from datetime import datetime
from typing import Dict, Callable, Any, List
from friday.scheduler.recurring import RecurringTask
from friday.scheduler.delayed import DelayedTask
from friday.scheduler.queue import PriorityTaskQueue

class TaskScheduler:
    def __init__(self, queue: PriorityTaskQueue):
        self.queue = queue
        self.recurring_tasks: List[RecurringTask] = []
        self.delayed_tasks: List[DelayedTask] = []
        self.task_callbacks: Dict[str, Callable[[], Any]] = {}
        self.is_running = False
        self._loop_task = None

    def register_task_callback(self, task_id: str, callback: Callable[[], Any]):
        self.task_callbacks[task_id] = callback

    def add_recurring_task(self, task_id: str, interval_seconds: float):
        self.recurring_tasks.append(RecurringTask(task_id=task_id, interval_seconds=interval_seconds))

    def add_delayed_task(self, task_id: str, run_at: datetime):
        self.delayed_tasks.append(DelayedTask(task_id=task_id, run_at=run_at))

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._loop_task = asyncio.create_task(self._scheduler_loop())

    def stop(self):
        self.is_running = False
        if self._loop_task:
            self._loop_task.cancel()

    async def _scheduler_loop(self):
        while self.is_running:
            now = datetime.utcnow()
            
            # Check recurring tasks
            for task in self.recurring_tasks:
                if task.is_due(now):
                    task.last_run = now
                    callback = self.task_callbacks.get(task.task_id)
                    if callback:
                        await self.queue.enqueue(2, callback)  # Priority 2 for recurring tasks

            # Check delayed tasks
            completed_delayed = []
            for task in self.delayed_tasks:
                if task.is_due(now):
                    callback = self.task_callbacks.get(task.task_id)
                    if callback:
                        await self.queue.enqueue(1, callback)  # Priority 1 (higher) for one-shots
                    completed_delayed.append(task)
                    
            for task in completed_delayed:
                self.delayed_tasks.remove(task)

            # Consume queue items
            while not self.queue.empty():
                priority, callback = await self.queue.dequeue()
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback()
                    else:
                        callback()
                except Exception:
                    pass
                finally:
                    self.queue.task_done()

            await asyncio.sleep(0.5)
