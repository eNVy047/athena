from __future__ import annotations

import asyncio
import logging
from typing import Callable, Coroutine, Any, Optional

logger = logging.getLogger("friday-agent")

class ActionScheduler:
    def __init__(self):
        self.queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def start(self, executor_callback: Callable[[Any], Coroutine[Any, Any, None]]) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._worker(executor_callback))
        logger.info("[ActionScheduler] Background worker queue started.")

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def schedule(self, action_request: Any) -> None:
        await self.queue.put(action_request)
        logger.debug("[ActionScheduler] Enqueued action request.")

    async def _worker(self, executor_callback: Callable[[Any], Coroutine[Any, Any, None]]) -> None:
        while self._running:
            try:
                request = await self.queue.get()
                await executor_callback(request)
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[ActionScheduler] Error executing scheduled action: {e}", exc_info=True)
