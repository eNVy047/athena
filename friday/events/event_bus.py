import asyncio
import logging
from typing import Dict, List, Callable, Any, Coroutine

logger = logging.getLogger(__name__)

class EventBus:
    """Core Event Bus for publish-subscribe pattern across perception and action layers."""
    def __init__(self):
        self._listeners: Dict[str, List[Callable[[Any], Coroutine[Any, Any, None]]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Any], Coroutine[Any, Any, None]]) -> None:
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    async def publish(self, event_type: str, event_data: Any) -> None:
        if event_type not in self._listeners:
            return
        
        logger.debug(f"Publishing event: {event_type}")
        tasks = []
        for listener in self._listeners[event_type]:
            tasks.append(asyncio.create_task(listener(event_data)))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
