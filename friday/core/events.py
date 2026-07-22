import asyncio
from typing import Callable, Any, Dict, List, Coroutine

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable[[Any], Coroutine[Any, Any, None]]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Any], Coroutine[Any, Any, None]]):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    async def publish(self, event_type: str, event_data: Any):
        if event_type not in self._listeners:
            return
        tasks = [listener(event_data) for listener in self._listeners[event_type]]
        await asyncio.gather(*tasks, return_exceptions=True)
