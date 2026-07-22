import logging
import subprocess
import sys
from typing import Dict, Any, List
from friday.perception.sensor import Sensor
from friday.perception.sensor_metadata import SensorMetadata, SensorStatus
from friday.perception.sensor_context import SensorContext
from friday.perception.sensor_result import SensorResult

logger = logging.getLogger(__name__)

class BluetoothSensor(Sensor):
    def __init__(self):
        metadata = SensorMetadata(
            name="bluetooth",
            description="Observes Bluetooth power and connected devices using macOS system_profiler",
            version="1.0.0",
            capabilities=["network.bluetooth_monitoring"],
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
            return SensorResult(success=False, error="Bluetooth monitoring only supported on macOS")

        try:
            cmd = ["system_profiler", "SPBluetoothDataType"]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=3.0)
            if process.returncode != 0:
                return SensorResult(success=False, error="Bluetooth profile query failed")

            output = process.stdout
            enabled = "Bluetooth Power: On" in output
            
            # Extract names of connected devices
            connected_devices = []
            current_device = None
            is_connected = False
            
            for line in output.splitlines():
                stripped = line.strip()
                if line.startswith(" " * 8) and stripped.endswith(":"):
                    current_device = stripped[:-1]
                if "Connected: Yes" in line and current_device:
                    connected_devices.append(current_device)

            return SensorResult(success=True, data={
                "enabled": enabled,
                "connected_devices": connected_devices
            })
        except Exception as e:
            logger.error(f"Failed to query Bluetooth: {e}")
            return SensorResult(success=False, error=str(e))
