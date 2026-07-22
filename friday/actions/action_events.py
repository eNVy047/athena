from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional
from friday.events.event_bus import EventBus
from friday.events.event_types import Event
from friday.actions.action_models import ActionRequest
from friday.actions.action_result import ActionResult

logger = logging.getLogger("friday-agent")

ACTION_STARTED = "action.started"
ACTION_COMPLETED = "action.completed"
ACTION_FAILED = "action.failed"

class ActionEvents:
    def __init__(self, event_bus: Optional[EventBus] = None):
        self.event_bus = event_bus

    async def publish_started(self, request: ActionRequest) -> None:
        if not self.event_bus:
            return
        event = Event(
            event_type=ACTION_STARTED,
            data={"action_type": request.action_type.value, "command": request.command},
            timestamp=datetime.utcnow()
        )
        await self.event_bus.publish(ACTION_STARTED, event)

    async def publish_completed(self, request: ActionRequest, result: ActionResult) -> None:
        if not self.event_bus:
            return
        event = Event(
            event_type=ACTION_COMPLETED,
            data={
                "action_name": f"{request.action_type.value}.{request.command}",
                "success": result.success,
                "result": str(result.output) if result.success else result.error
            },
            timestamp=datetime.utcnow()
        )
        await self.event_bus.publish(ACTION_COMPLETED, event)
