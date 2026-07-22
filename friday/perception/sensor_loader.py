import logging
from typing import List
from friday.perception.sensor import Sensor
from friday.perception.sensor_registry import SensorRegistry

logger = logging.getLogger(__name__)

class SensorLoader:
    @staticmethod
    def load_enabled_sensors(registry: SensorRegistry, config: dict) -> List[Sensor]:
        """Loads and instantiates production sensors based on environment config flags."""
        loaded = []

        # Production sensors imports
        from friday.perception.sensors.camera import CameraSensor
        from friday.perception.sensors.screen import ScreenSensor
        from friday.perception.sensors.microphone import MicrophoneSensor
        from friday.perception.sensors.filesystem import FilesystemSensor
        from friday.perception.sensors.clipboard import ClipboardSensor
        from friday.perception.sensors.window import WindowSensor
        from friday.perception.sensors.process import ProcessSensor
        from friday.perception.sensors.battery import BatterySensor
        from friday.perception.sensors.network import NetworkSensor
        from friday.perception.sensors.usb import UsbSensor
        from friday.perception.sensors.wifi import WifiSensor
        from friday.perception.sensors.bluetooth import BluetoothSensor
        from friday.perception.sensors.system import SystemSensor
        from friday.perception.sensors.notifications import NotificationsSensor

        sensor_mapping = {
            "camera": (CameraSensor, "CAMERA_ENABLED"),
            "screen": (ScreenSensor, "SCREEN_ENABLED"),
            "microphone": (MicrophoneSensor, "MICROPHONE_ENABLED"),
            "filesystem": (FilesystemSensor, "FILESYSTEM_ENABLED"),
            "clipboard": (ClipboardSensor, "CLIPBOARD_ENABLED"),
            "window": (WindowSensor, "WINDOW_MONITOR_ENABLED"),
            "process": (ProcessSensor, "PROCESS_MONITOR_ENABLED"),
            "battery": (BatterySensor, "BATTERY_MONITOR_ENABLED"),
            "network": (NetworkSensor, "NETWORK_MONITOR_ENABLED"),
            "usb": (UsbSensor, "USB_MONITOR_ENABLED"),
            "wifi": (WifiSensor, "WIFI_MONITOR_ENABLED"),
            "bluetooth": (BluetoothSensor, "BLUETOOTH_MONITOR_ENABLED"),
            "system": (SystemSensor, "SYSTEM_MONITOR_ENABLED"),
            "notifications": (NotificationsSensor, "NOTIFICATIONS_MONITOR_ENABLED")
        }

        # Always enable system metrics monitor by default if not set
        if "SYSTEM_MONITOR_ENABLED" not in config:
            config["SYSTEM_MONITOR_ENABLED"] = "true"
        if "NOTIFICATIONS_MONITOR_ENABLED" not in config:
            config["NOTIFICATIONS_MONITOR_ENABLED"] = "true"

        for name, (sensor_class, env_flag) in sensor_mapping.items():
            enabled_str = str(config.get(env_flag, "false")).lower()
            if enabled_str == "true":
                try:
                    sensor_instance = sensor_class()
                    registry.register(sensor_instance)
                    loaded.append(sensor_instance)
                    logger.info(f"Loaded production sensor: {name}")
                except Exception as e:
                    logger.error(f"Failed to load production sensor {name}: {e}")

        return loaded
