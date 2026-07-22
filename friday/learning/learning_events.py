from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from friday.events.event_types import Event

LEARNING_REFLECTION_COMPLETED = "learning.reflection_completed"
LEARNING_PATTERN_DETECTED = "learning.pattern_detected"
LEARNING_PREFERENCE_UPDATED = "learning.preference_updated"
LEARNING_WORKFLOW_OPTIMIZED = "learning.workflow_optimized"
LEARNING_ERROR = "learning.error"

@dataclass
class LearningEvent(Event):
    """Base event for learning system."""
    session_id: str = ""
    source: str = ""
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ReflectionCompletedEvent(LearningEvent):
    """Fired when reflection completes."""
    insights: list = field(default_factory=list)

@dataclass
class PreferenceUpdatedEvent(LearningEvent):
    """Fired when a user preference is updated implicitly."""
    category: str = ""
    value: Any = None
