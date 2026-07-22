import logging
import psutil
from typing import Dict, Any, List
from friday.perception.sensor import Sensor
from friday.perception.sensor_metadata import SensorMetadata, SensorStatus
from friday.perception.sensor_context import SensorContext
from friday.perception.sensor_result import SensorResult

logger = logging.getLogger(__name__)

class ProcessSensor(Sensor):
    def __init__(self):
        metadata = SensorMetadata(
            name="process",
            description="Observes active OS processes using psutil",
            version="1.0.0",
            capabilities=["system.process_tracking"],
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
            processes = []
            # Grab top 10 processes by CPU consumption to prevent overhead
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'create_time']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass

            # Sort by cpu_percent descending
            processes = sorted(processes, key=lambda p: p.get('cpu_percent', 0.0) or 0.0, reverse=True)[:10]

            return SensorResult(success=True, data={
                "top_processes": processes,
                "total_process_count": len(psutil.pids())
            })
        except Exception as e:
            logger.error(f"Process sensor polling failed: {e}")
            return SensorResult(success=False, error=str(e))
