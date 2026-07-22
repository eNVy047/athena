from __future__ import annotations

import asyncio
import logging
from typing import Dict, Callable, Coroutine, Any

logger = logging.getLogger("friday-agent")

class WorkflowScheduler:
    def __init__(self):
        self.scheduled_tasks: Dict[str, asyncio.Task] = {}

    def schedule_recurring(self, workflow_id: str, interval: float, run_callback: Callable[[], Coroutine[Any, Any, None]]) -> None:
        """Schedules a workflow to execute at a recurring interval (seconds)."""
        self.cancel_schedule(workflow_id)
        
        async def loop():
            while True:
                await asyncio.sleep(interval)
                try:
                    await run_callback()
                except Exception as e:
                    logger.error(f"[WorkflowScheduler] Recurring run for {workflow_id} failed: {e}")
                    
        self.scheduled_tasks[workflow_id] = asyncio.create_task(loop())
        logger.debug(f"[WorkflowScheduler] Scheduled workflow {workflow_id} every {interval}s")

    def cancel_schedule(self, workflow_id: str) -> None:
        if workflow_id in self.scheduled_tasks:
            self.scheduled_tasks[workflow_id].cancel()
            del self.scheduled_tasks[workflow_id]

    def stop(self) -> None:
        for t in list(self.scheduled_tasks.values()):
            t.cancel()
        self.scheduled_tasks.clear()
