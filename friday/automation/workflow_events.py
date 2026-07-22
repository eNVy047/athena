from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional
from friday.events.event_bus import EventBus
from friday.events.event_types import Event

logger = logging.getLogger("friday-agent")

WORKFLOW_STARTED = "workflow.started"
WORKFLOW_COMPLETED = "workflow.completed"
WORKFLOW_FAILED = "workflow.failed"

class WorkflowEvents:
    def __init__(self, event_bus: Optional[EventBus] = None):
        self.event_bus = event_bus

    async def publish_started(self, workflow_id: str) -> None:
        if not self.event_bus:
            return
        event = Event(
            event_type=WORKFLOW_STARTED,
            data={"workflow_id": workflow_id},
            timestamp=datetime.utcnow()
        )
        await self.event_bus.publish(WORKFLOW_STARTED, event)

    async def publish_completed(self, workflow_id: str, success: bool, error: Optional[str] = None) -> None:
        if not self.event_bus:
            return
        event_type = WORKFLOW_COMPLETED if success else WORKFLOW_FAILED
        event = Event(
            event_type=event_type,
            data={"workflow_id": workflow_id, "success": success, "error": error},
            timestamp=datetime.utcnow()
        )
        await self.event_bus.publish(event_type, event)
