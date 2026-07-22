from __future__ import annotations

import logging
from typing import Dict, List, Callable, Coroutine, Any, Optional
from friday.events.event_bus import EventBus
from friday.events.event_types import Event

logger = logging.getLogger("friday-agent")

class TriggerEngine:
    def __init__(self, event_bus: Optional[EventBus] = None):
        self.event_bus = event_bus
        self.trigger_registry: Dict[str, List[Callable[[Event], Coroutine[Any, Any, None]]]] = {}

    def register_trigger(self, event_type: str, callback: Callable[[Event], Coroutine[Any, Any, None]]) -> None:
        if event_type not in self.trigger_registry:
            self.trigger_registry[event_type] = []
        self.trigger_registry[event_type].append(callback)
        logger.debug(f"[TriggerEngine] Registered trigger callback for event: {event_type}")

        if self.event_bus:
            # Subscribe trigger engine listener to event bus
            self.event_bus.subscribe(event_type, self._handle_event)

    async def _handle_event(self, event: Event) -> None:
        callbacks = self.trigger_registry.get(event.event_type, [])
        for cb in callbacks:
            try:
                await cb(event)
            except Exception as e:
                logger.error(f"[TriggerEngine] Error firing trigger callback for event {event.event_type}: {e}")
                
    def clear(self) -> None:
        self.trigger_registry.clear()
