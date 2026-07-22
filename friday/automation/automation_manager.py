from __future__ import annotations

import logging
from typing import Any, Optional
from friday.automation.workflow_manager import WorkflowManager
from friday.automation.trigger_engine import TriggerEngine

logger = logging.getLogger("friday-agent")

class AutomationManager:
    def __init__(self, action_manager: Any, security_manager: Optional[Any] = None, event_bus: Optional[Any] = None, memory_manager: Optional[Any] = None):
        self.workflow_manager = WorkflowManager(action_manager, security_manager, event_bus, memory_manager)
        self.trigger_engine = TriggerEngine(event_bus)

    def initialize(self) -> None:
        logger.info("[AutomationManager] Automation and Workflow Engine successfully initialized.")

    def shutdown(self) -> None:
        self.workflow_manager.shutdown()
        self.trigger_engine.clear()
        logger.info("[AutomationManager] Automation and Workflow Engine shut down.")
