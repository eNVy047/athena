import logging
from typing import Dict, Any
from mss import mss
from friday.perception.sensor import Sensor
from friday.perception.sensor_metadata import SensorMetadata, SensorStatus
from friday.perception.sensor_context import SensorContext
from friday.perception.sensor_result import SensorResult

logger = logging.getLogger(__name__)

class ScreenSensor(Sensor):
    def __init__(self):
        metadata = SensorMetadata(
            name="screen",
            description="Observes desktop screens using mss",
            version="1.0.0",
            capabilities=["vision.screen_capture"],
            required_permissions=[]
        )
        super().__init__(metadata)
        self.sct = None

    async def initialize(self, context: SensorContext) -> None:
        await super().initialize(context)

    async def start(self) -> None:
        await super().start()
        self.sct = mss()

    async def pause(self) -> None:
        await super().pause()

    async def resume(self) -> None:
        await super().resume()
        if not self.sct:
            self.sct = mss()

    async def stop(self) -> None:
        await super().stop()
        if self.sct:
            self.sct.close()
            self.sct = None

    async def health_check(self) -> bool:
        return self.sct is not None

    async def observe(self) -> SensorResult:
        if self.status != SensorStatus.RUNNING:
            return SensorResult(success=False, error="Sensor not running")

        if not self.sct:
            self.sct = mss()

        try:
            # Capture the first monitor (which usually represents the primary desktop monitor)
            monitor = self.sct.monitors[1]
            screenshot = self.sct.grab(monitor)
            # Convert screenshot PNG to bytes
            import mss.tools
            png_bytes = mss.tools.to_png(screenshot.rgb, screenshot.size)
            return SensorResult(success=True, data={
                "bytes": png_bytes,
                "width": screenshot.width,
                "height": screenshot.height
            })
        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
            return SensorResult(success=False, error=str(e))
