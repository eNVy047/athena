import asyncio
import logging
from typing import Dict, List, Callable, Coroutine, Any

logger = logging.getLogger(__name__)

class LifecycleCoordinator:
    """Manages Phase-based bootstrap initialization and teardown of Friday subsystems."""
    def __init__(self):
        self._startup_actions: Dict[str, Callable[[], Coroutine[Any, Any, None]]] = {}
        self._shutdown_actions: Dict[str, Callable[[], Coroutine[Any, Any, None]]] = {}
        self._bootstrap_order: List[str] = []
        self.is_running = False

    def register_subsystem(
        self, 
        name: str, 
        startup: Callable[[], Coroutine[Any, Any, None]], 
        shutdown: Callable[[], Coroutine[Any, Any, None]]
    ) -> None:
        self._startup_actions[name] = startup
        self._shutdown_actions[name] = shutdown
        if name not in self._bootstrap_order:
            self._bootstrap_order.append(name)

    def set_bootstrap_order(self, order: List[str]) -> None:
        self._bootstrap_order = [name for name in order if name in self._startup_actions]

    async def startup(self) -> None:
        if self.is_running:
            return
        
        logger.info("Starting Friday Subsystems...")
        for name in self._bootstrap_order:
            logger.info(f"Initializing subsystem: {name}")
            await self._startup_actions[name]()
        self.is_running = True
        logger.info("Friday Core subsystems initialized.")

    async def shutdown(self) -> None:
        if not self.is_running:
            return

        logger.info("Initiating system shutdown sequence...")
        for name in reversed(self._bootstrap_order):
            logger.info(f"Terminating subsystem: {name}")
            try:
                await self._shutdown_actions[name]()
            except Exception as e:
                logger.error(f"Error during subsystem shutdown {name}: {e}")
        self.is_running = False
        logger.info("Friday Core shutdown complete.")
