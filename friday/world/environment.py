from typing import Dict, Any, List, Optional

class EnvironmentManager:
    def __init__(self):
        self.os_type = "macOS"
        self.hardware_info: Dict[str, Any] = {
            "cpu": "Unknown CPU",
            "gpu": "Unknown GPU",
            "ram_total_gb": 16.0,
            "storage_total_gb": 512.0
        }
        self.displays: List[Dict[str, Any]] = []
        self.audio_devices: List[Dict[str, Any]] = []
        self.printers: List[str] = []
        self.internet_status = "connected"
        self.wifi_ssid: Optional[str] = None
        self.bluetooth_enabled = True
        self.power_state = "AC"

    def update_hardware(self, cpu: str, gpu: str, ram: float, storage: float) -> None:
        self.hardware_info = {
            "cpu": cpu,
            "gpu": gpu,
            "ram_total_gb": ram,
            "storage_total_gb": storage
        }

    def set_wifi(self, ssid: str) -> None:
        self.wifi_ssid = ssid

    def set_power(self, state: str) -> None:
        self.power_state = state

    def get_environment_info(self) -> Dict[str, Any]:
        return {
            "os": self.os_type,
            "hardware": self.hardware_info,
            "displays": self.displays,
            "audio_devices": self.audio_devices,
            "printers": self.printers,
            "internet_status": self.internet_status,
            "wifi_ssid": self.wifi_ssid,
            "bluetooth_enabled": self.bluetooth_enabled,
            "power_state": self.power_state
        }
