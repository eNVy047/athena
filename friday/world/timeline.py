import time
from typing import Dict, Any, List, Optional

class TimelineEvent:
    def __init__(self, event_id: str, timestamp: float, entity_id: str, action: str, details: Optional[Dict[str, Any]] = None):
        self.event_id = event_id
        self.timestamp = timestamp
        self.entity_id = entity_id
        self.action = action  # e.g., "creation", "modification", "accessed", "scheduled"
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "entity_id": self.entity_id,
            "action": self.action,
            "details": self.details
        }

class Timeline:
    def __init__(self):
        self._events: List[TimelineEvent] = []

    def record_event(self, entity_id: str, action: str, details: Optional[Dict[str, Any]] = None) -> TimelineEvent:
        event_id = f"evt_{int(time.time() * 1000)}"
        event = TimelineEvent(event_id, time.time(), entity_id, action, details)
        self._events.append(event)
        return event

    def get_history(self, entity_id: Optional[str] = None, action: Optional[str] = None) -> List[TimelineEvent]:
        events = sorted(self._events, key=lambda e: e.timestamp)
        if entity_id is not None:
            events = [e for e in events if e.entity_id == entity_id]
        if action is not None:
            events = [e for e in events if e.action == action]
        return events
