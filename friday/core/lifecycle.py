import asyncio
import logging
from friday.core.di import container
from friday.core.events import EventBus
from friday.core.resources import ResourceManager
from friday.core.tasks import BackgroundTaskManager

logger = logging.getLogger(__name__)

class LifecycleCoordinator:
    def __init__(self):
        self.event_bus = EventBus()
        self.resources = ResourceManager()
        self.tasks = BackgroundTaskManager()
        self.is_running = False

    async def startup(self):
        if self.is_running:
            return
        
        logger.info("Initializing Friday AI OS Core Subsystems...")
        
        # Register core managers with DI container
        container.register(EventBus, self.event_bus)
        container.register(ResourceManager, self.resources)
        container.register(BackgroundTaskManager, self.tasks)
        
        self.is_running = True
        await self.event_bus.publish("SystemStarted", {})
        logger.info("Friday AI OS Core Subsystems successfully initialized.")

    async def shutdown(self):
        if not self.is_running:
            return
        
        logger.info("Shutting down Friday AI OS Subsystems...")
        await self.event_bus.publish("ShutdownRequested", {})
        
        # 1. Shutdown background tasks
        await self.tasks.shutdown(timeout=5.0)
        
        # 2. Release allocated connections/subprocess handles
        await self.resources.shutdown()
        
        self.is_running = False
        logger.info("Friday AI OS shutdown complete.")

# Global instance
lifecycle = LifecycleCoordinator()
