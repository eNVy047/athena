import logging
import pyperclip
from friday.perception.sensor import Sensor
from friday.perception.sensor_metadata import SensorMetadata, SensorStatus
from friday.perception.sensor_context import SensorContext
from friday.perception.sensor_result import SensorResult

logger = logging.getLogger(__name__)

class ClipboardSensor(Sensor):
    def __init__(self):
        metadata = SensorMetadata(
            name="clipboard",
            description="Observes clipboard contents using pyperclip",
            version="1.0.0",
            capabilities=["system.clipboard_watch"],
            required_permissions=[]
        )
        super().__init__(metadata)
        self.last_content = ""

    async def initialize(self, context: SensorContext) -> None:
        await super().initialize(context)

    async def start(self) -> None:
        await super().start()
        try:
            self.last_content = pyperclip.paste()
        except Exception:
            self.last_content = ""

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

        try:
            current_content = pyperclip.paste()
            if current_content != self.last_content:
                self.last_content = current_content
                return SensorResult(success=True, data={
                    "changed": True,
                    "content": current_content
                })
            return SensorResult(success=True, data={"changed": False})
        except Exception as e:
            logger.error(f"Clipboard read failed: {e}")
            return SensorResult(success=False, error=str(e))
