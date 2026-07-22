import time
from typing import Dict, Any, List, Optional

class Observation:
    def __init__(
        self,
        observation_id: str,
        sensor_name: str,
        raw_data: Any,
        normalized_data: Any,
        confidence: float = 1.0,
        source: str = "environment",
        priority: int = 1,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = observation_id
        self.timestamp = time.time()
        self.sensor_name = sensor_name
        self.raw_data = raw_data
        self.normalized_data = normalized_data
        self.confidence = confidence
        self.source = source
        self.priority = priority
        self.tags = tags or []
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "sensor_name": self.sensor_name,
            "raw_data": self.raw_data,
            "normalized_data": self.normalized_data,
            "confidence": self.confidence,
            "source": self.source,
            "priority": self.priority,
            "tags": self.tags,
            "metadata": self.metadata
        }
