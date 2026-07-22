import logging
import asyncio
from friday.learning.learning_manager import LearningManager
from friday.learning.learning_context import LearningContext

logger = logging.getLogger(__name__)

class LearningScheduler:
    """Schedules background reflection cycles."""
    
    def __init__(self, manager: LearningManager, interval_seconds: int = 3600):
        self.manager = manager
        self.interval = interval_seconds
        self._running = False
        self._task = None
        
    def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._loop())
            
    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            
    async def _loop(self):
        logger.info(f"LearningScheduler started. Interval: {self.interval}s")
        while self._running:
            try:
                await asyncio.sleep(self.interval)
                context = LearningContext(session_id="background_scheduler", trigger_source="scheduled")
                await self.manager.run_reflection_cycle(context)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"LearningScheduler error: {e}")
