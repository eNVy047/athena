import logging
import platform
import psutil
from friday.perception.sensor import Sensor
from friday.perception.sensor_metadata import SensorMetadata, SensorStatus
from friday.perception.sensor_context import SensorContext
from friday.perception.sensor_result import SensorResult

logger = logging.getLogger(__name__)

class SystemSensor(Sensor):
    def __init__(self):
        metadata = SensorMetadata(
            name="system",
            description="Observes general OS version, CPU, RAM and disk capacities using psutil",
            version="1.0.0",
            capabilities=["system.metrics_polling"],
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
        return True

    async def observe(self) -> SensorResult:
        if self.status != SensorStatus.RUNNING:
            return SensorResult(success=False, error="Sensor not running")

        try:
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return SensorResult(success=True, data={
                "os": platform.system(),
                "os_release": platform.release(),
                "hostname": platform.node(),
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(),
                "memory_total_gb": mem.total / (1024**3),
                "memory_used_percent": mem.percent,
                "disk_total_gb": disk.total / (1024**3),
                "disk_used_percent": disk.percent
            })
        except Exception as e:
            logger.error(f"System metrics observation failed: {e}")
            return SensorResult(success=False, error=str(e))
