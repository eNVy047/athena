import asyncio
import logging
from typing import Optional

logger = logging.getLogger("friday-agent")


class MemoryScheduler:
    def __init__(self, memory_manager, interval_seconds: float = 300.0):
        self.memory_manager = memory_manager
        self.interval_seconds = interval_seconds
        self._task: Optional[asyncio.Task] = None
        self._running = False

    def start(self) -> None:
        """Starts the background consolidation and decay loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info(
            "[MemoryScheduler] Started memory consolidation/decay background loop."
        )

    async def stop(self) -> None:
        """Gracefully stops the background loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("[MemoryScheduler] Stopped background loop.")

    async def _loop(self) -> None:
        while self._running:
            try:
                await asyncio.sleep(self.interval_seconds)
                logger.info(
                    "[MemoryScheduler] Triggering periodic memory consolidation and decay."
                )
                await self.memory_manager.consolidate_memories()
                await self.memory_manager.apply_decay_and_forgetting()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(
                    f"[MemoryScheduler] Error in background loop: {e}", exc_info=True
                )
