import logging
from typing import Any
from friday.core.kernel.kernel import FridayKernel
from friday.events.event_bus import EventBus

class SkillContext:
    """Provides a safe sandboxed interface exposing core engines to running Skills."""
    def __init__(self, kernel: FridayKernel, event_bus: EventBus, logger_name: str):
        self.kernel = kernel
        self.event_bus = event_bus
        self.logger = logging.getLogger(logger_name)
        self.config = kernel.config

    def get_service(self, interface: Any) -> Any:
        return self.kernel.services.get(interface)
