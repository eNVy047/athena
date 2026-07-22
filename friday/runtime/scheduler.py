import asyncio
import logging
from typing import Dict, Any, Callable, Coroutine, List
from datetime import datetime

logger = logging.getLogger(__name__)

class Scheduler:
    """Manages scheduled, cron, and periodic background execution loops."""
    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._loop_task: asyncio.Task | None = None

    def schedule_cron(self, job_id: str, cron_expr: str, callback: Callable[[], Coroutine[Any, Any, None]]) -> None:
        self._jobs[job_id] = {
            "type": "cron",
            "expression": cron_expr,
            "callback": callback,
            "last_run": None
        }
        logger.info(f"Scheduled cron job: {job_id} ({cron_expr})")

    def schedule_interval(self, job_id: str, interval_seconds: float, callback: Callable[[], Coroutine[Any, Any, None]]) -> None:
        self._jobs[job_id] = {
            "type": "interval",
            "interval": interval_seconds,
            "callback": callback,
            "last_run": datetime.utcnow()
        }
        logger.info(f"Scheduled interval job: {job_id} (every {interval_seconds}s)")

    def start(self) -> None:
        self._loop_task = asyncio.create_task(self._scheduler_loop())

    async def stop(self) -> None:
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass

    async def _scheduler_loop(self) -> None:
        while True:
            await asyncio.sleep(1.0)
            now = datetime.utcnow()
            for job_id, job in list(self._jobs.items()):
                if job["type"] == "interval":
                    elapsed = (now - job["last_run"]).total_seconds()
                    if elapsed >= job["interval"]:
                        job["last_run"] = now
                        asyncio.create_task(job["callback"]())
