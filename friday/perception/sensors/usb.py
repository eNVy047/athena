import logging
import subprocess
import sys
from typing import Dict, Any, List
from friday.perception.sensor import Sensor
from friday.perception.sensor_metadata import SensorMetadata, SensorStatus
from friday.perception.sensor_context import SensorContext
from friday.perception.sensor_result import SensorResult

logger = logging.getLogger(__name__)

class UsbSensor(Sensor):
    def __init__(self):
        metadata = SensorMetadata(
            name="usb",
            description="Observes connected USB devices using macOS system_profiler",
            version="1.0.0",
            capabilities=["system.usb_polling"],
            required_permissions=[]
        )
        super().__init__(metadata)
        self.last_devices = []

    async def initialize(self, context: SensorContext) -> None:
        await super().initialize(context)

    async def start(self) -> None:
        await super().start()
        self.last_devices = self._get_usb_devices()

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

        current_devices = self._get_usb_devices()
        
        # Check if changed
        changed = set(current_devices) != set(self.last_devices)
        self.last_devices = current_devices

        return SensorResult(success=True, data={
            "changed": changed,
            "connected_devices": current_devices
        })

    def _get_usb_devices(self) -> List[str]:
        if sys.platform != "darwin":
            return []

        try:
            # Query USB info from system profiler
            cmd = ["system_profiler", "SPUSBDataType"]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=3.0)
            if process.returncode != 0:
                return []

            devices = []
            for line in process.stdout.splitlines():
                if "Product ID:" in line or "Vendor ID:" in line or "Serial Number:" in line:
                    continue
                # Line containing device name starts with 12 spaces in System Profiler USB output
                stripped = line.strip()
                if line.startswith(" " * 8) and not line.startswith(" " * 9) and stripped and not stripped.endswith(":"):
                    devices.append(stripped)
            return sorted(list(set(devices)))
        except Exception as e:
            logger.error(f"Failed to query USB devices: {e}")
            return []
