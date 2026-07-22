from typing import Dict, List, Optional
from friday.perception.sensor import Sensor

class SensorRegistry:
    def __init__(self):
        self._sensors: Dict[str, Sensor] = {}

    def register(self, sensor: Sensor) -> None:
        self._sensors[sensor.metadata.name] = sensor

    def unregister(self, name: str) -> Optional[Sensor]:
        return self._sensors.pop(name, None)

    def get(self, name: str) -> Optional[Sensor]:
        return self._sensors.get(name)

    def list_all(self) -> List[Sensor]:
        return list(self._sensors.values())

    def get_by_capability(self, capability: str) -> List[Sensor]:
        return [s for s in self._sensors.values() if capability in s.metadata.capabilities]
