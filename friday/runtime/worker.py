import asyncio
import logging
from typing import Dict, Any, Callable, Coroutine
from friday.core.cognition.models import Task, TaskStatus

logger = logging.getLogger(__name__)

class Worker:
    """Async worker instance consuming tasks and executing individual action steps."""
    def __init__(self, worker_id: str, action_handlers: Dict[str, Callable[[Dict[str, Any]], Coroutine[Any, Any, Any]]]):
        self.worker_id = worker_id
        self.action_handlers = action_handlers
        self.is_idle = True

    async def execute_task(self, task: Task) -> bool:
        self.is_idle = False
        task.status = TaskStatus.RUNNING
        logger.info(f"Worker {self.worker_id} started task {task.name}")

        success = True
        for step in task.steps:
            handler = self.action_handlers.get(step.action_name)
            if not handler:
                logger.error(f"No action handler for {step.action_name} registered.")
                success = False
                break
            try:
                await handler(step.parameters)
            except Exception as e:
                logger.error(f"Worker step failure in task {task.name}: {e}")
                success = False
                break

        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        self.is_idle = True
        return success
