import logging
import subprocess
import sys
import re
from friday.perception.sensor import Sensor
from friday.perception.sensor_metadata import SensorMetadata, SensorStatus
from friday.perception.sensor_context import SensorContext
from friday.perception.sensor_result import SensorResult

logger = logging.getLogger(__name__)

class WifiSensor(Sensor):
    def __init__(self):
        metadata = SensorMetadata(
            name="wifi",
            description="Observes Wi-Fi network connection properties on macOS",
            version="1.0.0",
            capabilities=["network.wifi_monitoring"],
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
            return SensorResult(success=False, error="Wi-Fi monitoring only supported on macOS")

        try:
            cmd = ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=2.0)
            if process.returncode != 0:
                return SensorResult(success=False, error="Airport command failed or Wi-Fi is disabled")

            output = process.stdout
            ssid = None
            bssid = None
            rssi = None
            
            ssid_match = re.search(r"\bSSID:\s*(.+)", output)
            if ssid_match:
                ssid = ssid_match.group(1).strip()
            
            bssid_match = re.search(r"\bBSSID:\s*(.+)", output)
            if bssid_match:
                bssid = bssid_match.group(1).strip()
                
            rssi_match = re.search(r"\bagrCtlRSSI:\s*(-\d+)", output)
            if rssi_match:
                rssi = int(rssi_match.group(1).strip())

            return SensorResult(success=True, data={
                "connected": ssid is not None,
                "ssid": ssid,
                "bssid": bssid,
                "rssi": rssi
            })
        except Exception as e:
            logger.error(f"Failed to query Wi-Fi status: {e}")
            return SensorResult(success=False, error=str(e))
