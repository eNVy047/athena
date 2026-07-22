from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional
from friday.events.event_bus import EventBus
from friday.events.event_types import Event

logger = logging.getLogger("friday-agent")

AGENT_STARTED = "agent.started"
AGENT_COMPLETED = "agent.completed"
AGENT_FAILED = "agent.failed"

class AgentEvents:
    def __init__(self, event_bus: Optional[EventBus] = None):
        self.event_bus = event_bus

    async def publish_started(self, conversation_id: str, request_id: str) -> None:
        if not self.event_bus:
            return
        event = Event(
            event_type=AGENT_STARTED,
            data={"conversation_id": conversation_id, "request_id": request_id},
            timestamp=datetime.utcnow()
        )
        await self.event_bus.publish(AGENT_STARTED, event)

    async def publish_completed(self, conversation_id: str, success: bool, error: Optional[str] = None) -> None:
        if not self.event_bus:
            return
        event_type = AGENT_COMPLETED if success else AGENT_FAILED
        event = Event(
            event_type=event_type,
            data={"conversation_id": conversation_id, "success": success, "error": error},
            timestamp=datetime.utcnow()
        )
        await self.event_bus.publish(event_type, event)
