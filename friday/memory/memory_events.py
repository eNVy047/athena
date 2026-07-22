import logging
from datetime import datetime
from typing import Optional
from friday.events.event_bus import EventBus
from friday.events.event_types import Event
from friday.memory.memory_models import MemoryEntry

logger = logging.getLogger("friday-agent")

# Memory Event Types
MEMORY_STORED = "memory.stored"
MEMORY_RECALLED = "memory.recalled"
MEMORY_DECAYED = "memory.decayed"
MEMORY_CONSOLIDATED = "memory.consolidated"


class MemoryEvents:
    def __init__(self, event_bus: Optional[EventBus] = None):
        self.event_bus = event_bus

    async def publish_stored(self, entry: MemoryEntry) -> None:
        if not self.event_bus:
            return
        event = Event(
            event_type=MEMORY_STORED,
            data={
                "memory_id": entry.id,
                "content": entry.content,
                "memory_type": entry.memory_type.value,
            },
            timestamp=datetime.utcnow(),
        )
        await self.event_bus.publish(MEMORY_STORED, event)

    async def publish_recalled(self, query: str, results_count: int) -> None:
        if not self.event_bus:
            return
        event = Event(
            event_type=MEMORY_RECALLED,
            data={"query": query, "results_count": results_count},
            timestamp=datetime.utcnow(),
        )
        await self.event_bus.publish(MEMORY_RECALLED, event)
