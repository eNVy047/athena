from dataclasses import dataclass, field
from typing import Dict, Any
import time

@dataclass
class LearningContext:
    """Contextual information for a learning/reflection process."""
    session_id: str
    trigger_source: str  # 'scheduled', 'manual', 'event'
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
