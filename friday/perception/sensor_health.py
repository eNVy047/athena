import time
from typing import Dict, Any

class SensorHealth:
    def __init__(self, sensor_name: str):
        self.sensor_name = sensor_name
        self.is_alive = True
        self.last_heartbeat = time.time()
        self.error_count = 0
        self.latency_ms = 0.0
        self.dropped_observations = 0
        self.restart_count = 0

    def record_heartbeat(self, latency_ms: float = 0.0) -> None:
        self.last_heartbeat = time.time()
        self.is_alive = True
        self.latency_ms = latency_ms

    def record_error(self) -> None:
        self.error_count += 1
        self.is_alive = False

    def record_drop(self) -> None:
        self.dropped_observations += 1

    def record_restart(self) -> None:
        self.restart_count += 1
        self.is_alive = True
        self.error_count = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sensor_name": self.sensor_name,
            "is_alive": self.is_alive,
            "last_heartbeat": self.last_heartbeat,
            "error_count": self.error_count,
            "latency_ms": self.latency_ms,
            "dropped_observations": self.dropped_observations,
            "restart_count": self.restart_count
        }
