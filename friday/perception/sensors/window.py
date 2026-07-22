import logging
import subprocess
import sys
from friday.perception.sensor import Sensor
from friday.perception.sensor_metadata import SensorMetadata, SensorStatus
from friday.perception.sensor_context import SensorContext
from friday.perception.sensor_result import SensorResult

logger = logging.getLogger(__name__)

class WindowSensor(Sensor):
    def __init__(self):
        metadata = SensorMetadata(
            name="window",
            description="Observes active window details on macOS",
            version="1.0.0",
            capabilities=["system.window_monitoring"],
            required_permissions=[]
        )
        super().__init__(metadata)

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
        return sys.platform == "darwin"

    async def observe(self) -> SensorResult:
        if self.status != SensorStatus.RUNNING:
            return SensorResult(success=False, error="Sensor not running")

        if sys.platform != "darwin":
            return SensorResult(success=False, error="Window monitoring only supported on macOS")

        try:
            # Query active application using AppleScript
            app_cmd = ["osascript", "-e", 'tell application "System Events" to get name of first process whose frontmost is true']
            app_process = subprocess.run(app_cmd, capture_output=True, text=True, timeout=1.0)
            app_name = app_process.stdout.strip() if app_process.returncode == 0 else "Unknown Application"

            # Query active window title
            title_cmd = ["osascript", "-e", f'tell application "System Events" to tell process "{app_name}" to get name of window 1']
            title_process = subprocess.run(title_cmd, capture_output=True, text=True, timeout=1.0)
            window_title = title_process.stdout.strip() if title_process.returncode == 0 else "Unknown Title"

            return SensorResult(success=True, data={
                "application": app_name,
                "window_title": window_title,
                "pid": None  # AppleScript frontmost process PID lookup is optional
            })
        except Exception as e:
            logger.error(f"Failed to query active window on macOS: {e}")
            return SensorResult(success=False, error=str(e))
