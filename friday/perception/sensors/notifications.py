import logging
import sys
from typing import Dict, Any, List
from friday.perception.sensor import Sensor
from friday.perception.sensor_metadata import SensorMetadata, SensorStatus
from friday.perception.sensor_context import SensorContext
from friday.perception.sensor_result import SensorResult

logger = logging.getLogger(__name__)

class NotificationsSensor(Sensor):
    def __init__(self):
        metadata = SensorMetadata(
            name="notifications",
            description="Observes system notifications notifications",
            version="1.0.0",
            capabilities=["system.notifications_watch"],
            required_permissions=[]
        )
        super().__init__(metadata)
        self.notification_queue = []

    async def initialize(self, context: SensorContext) -> None:
        await super().initialize(context)

    async def start(self) -> None:
        await super().start()

    async def pause(self) -> None:
        await super().pause()

    async def resume(self) -> None:
        await super().resume()

    async def stop(self) -> None:
        await super().stop()

    async def health_check(self) -> bool:
        return True

    async def observe(self) -> SensorResult:
        if self.status != SensorStatus.RUNNING:
            return SensorResult(success=False, error="Sensor not running")

        # Returns notifications queue and flushes
        events = list(self.notification_queue)
        self.notification_queue.clear()
        
        return SensorResult(success=True, data={
            "notifications": events
        })

    def inject_notification(self, title: str, subtitle: str, message: str) -> None:
        """Extension point allowing other background processes or plugins to inject system notifications."""
        self.notification_queue.append({
            "title": title,
            "subtitle": subtitle,
            "message": message
        })
