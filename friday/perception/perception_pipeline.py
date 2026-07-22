import time
import logging
from typing import Dict, Any, List, Optional
from friday.perception.sensor import Sensor
from friday.perception.observation import Observation
from friday.perception.observation_buffer import ObservationBuffer
from friday.perception.observation_filter import ObservationFilter
from friday.perception.observation_validator import ObservationValidator
from friday.perception.observation_router import ObservationRouter
from friday.events.event_bus import EventBus

logger = logging.getLogger(__name__)

class PerceptionPipeline:
    def __init__(self, event_bus: EventBus, min_confidence: float = 0.5):
        self.event_bus = event_bus
        self.buffer = ObservationBuffer(max_size=100)
        self.filter = ObservationFilter(min_confidence)
        self.validator = ObservationValidator()
        self.router = ObservationRouter(self.event_bus)

    async def process_sensor_reading(self, sensor_name: str, raw_data: Any, confidence: float = 1.0) -> Optional[Observation]:
        # 1. Normalize
        normalized_data = self._normalize(sensor_name, raw_data)
        
        # 2. Build Observation envelope
        observation_id = f"obs_{sensor_name}_{int(time.time() * 1000)}"
        observation = Observation(
            observation_id=observation_id,
            sensor_name=sensor_name,
            raw_data=raw_data,
            normalized_data=normalized_data,
            confidence=confidence
        )

        # 3. Validate
        if not self.validator.validate(observation):
            logger.warning(f"Invalid observation format dropped for sensor: {sensor_name}")
            return None

        # 4. Filter
        if not self.filter.should_allow(observation):
            logger.debug(f"Observation filtered/dropped for sensor: {sensor_name}")
            return None

        # 5. Buffer
        self.buffer.append(observation)

        # 6. Route
        await self.router.route(observation)

        return observation

    def _normalize(self, sensor_name: str, raw_data: Any) -> Dict[str, Any]:
        """Normalizes raw input from different sensors to a consistent metadata shape."""
        normalized = {
            "sensor": sensor_name,
            "timestamp": time.time(),
            "payload": {}
        }
        
        if sensor_name == "camera":
            normalized["payload"] = {
                "has_video": True,
                "frame_details": raw_data.get("frame_id", "unknown")
            }
        elif sensor_name == "voice":
            normalized["payload"] = {
                "text": raw_data.get("transcript", ""),
                "speech_detected": True
            }
        elif sensor_name == "screen":
            normalized["payload"] = {
                "screenshot": raw_data.get("screenshot_id", "")
            }
        elif sensor_name == "usb":
            normalized["payload"] = {
                "devices": [dev.get("name") for dev in raw_data.get("connected_devices", [])]
            }
        elif sensor_name == "network":
            normalized["payload"] = {
                "connected": True,
                "ssid": raw_data.get("ssid", "")
            }
        elif sensor_name == "filesystem":
            normalized["payload"] = {
                "file": raw_data.get("modified_file", ""),
                "action": raw_data.get("action", "")
            }
        else:
            normalized["payload"] = {"raw": str(raw_data)}
            
        return normalized
