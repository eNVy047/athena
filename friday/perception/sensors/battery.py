import logging
import psutil
from friday.perception.sensor import Sensor
from friday.perception.sensor_metadata import SensorMetadata, SensorStatus
from friday.perception.sensor_context import SensorContext
from friday.perception.sensor_result import SensorResult

logger = logging.getLogger(__name__)

class BatterySensor(Sensor):
    def __init__(self):
        metadata = SensorMetadata(
            name="battery",
            description="Observes battery percentage, source, and state using psutil",
            version="1.0.0",
            capabilities=["system.battery_monitoring"],
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
        return psutil.sensors_battery() is not None

    async def observe(self) -> SensorResult:
        if self.status != SensorStatus.RUNNING:
            return SensorResult(success=False, error="Sensor not running")

        try:
            battery = psutil.sensors_battery()
            if not battery:
                return SensorResult(success=True, data={"has_battery": False})

            return SensorResult(success=True, data={
                "has_battery": True,
                "percent": battery.percent,
                "power_plugged": battery.power_plugged,
                "secsleft": battery.secsleft
            })
        except Exception as e:
            logger.error(f"Battery observation failed: {e}")
            return SensorResult(success=False, error=str(e))
