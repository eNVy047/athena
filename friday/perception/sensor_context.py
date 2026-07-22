from typing import Dict, Any
from friday.events.event_bus import EventBus

class SensorContext:
    def __init__(self, event_bus: EventBus, config: Dict[str, Any]):
        self.event_bus = event_bus
        self.config = config
