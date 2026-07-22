import logging
import psutil
from typing import Dict, Any, List
from friday.perception.sensor import Sensor
from friday.perception.sensor_metadata import SensorMetadata, SensorStatus
from friday.perception.sensor_context import SensorContext
from friday.perception.sensor_result import SensorResult

logger = logging.getLogger(__name__)

class NetworkSensor(Sensor):
    def __init__(self):
        metadata = SensorMetadata(
            name="network",
            description="Observes network adapters and traffic using psutil",
            version="1.0.0",
            capabilities=["network.status_polling"],
            required_permissions=[]
        )
        super().__init__(metadata)
        self.last_sent = 0
        self.last_recv = 0

    async def initialize(self, context: SensorContext) -> None:
        await super().initialize(context)

    async def start(self) -> None:
        await super().start()
        try:
            io = psutil.net_io_counters()
            self.last_sent = io.bytes_sent
            self.last_recv = io.bytes_recv
        except Exception:
            self.last_sent = 0
            self.last_recv = 0

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
            io = psutil.net_io_counters()
            sent_diff = io.bytes_sent - self.last_sent
            recv_diff = io.bytes_recv - self.last_recv

            self.last_sent = io.bytes_sent
            self.last_recv = io.bytes_recv

            # Get interfaces addresses
            interfaces = {}
            for name, addrs in psutil.net_if_addrs().items():
                interfaces[name] = [addr.address for addr in addrs if addr.family.name == "AF_INET"]

            return SensorResult(success=True, data={
                "bytes_sent_delta": sent_diff,
                "bytes_recv_delta": recv_diff,
                "interfaces": interfaces
            })
        except Exception as e:
            logger.error(f"Network observation failed: {e}")
            return SensorResult(success=False, error=str(e))
