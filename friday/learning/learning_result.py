from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class LearningResult:
    """Outcome of a learning or reflection process."""
    success: bool
    insights_generated: List[str] = field(default_factory=list)
    patterns_detected: int = 0
    preferences_updated: int = 0
    workflows_optimized: int = 0
    duration_ms: float = 0.0
    error: Optional[str] = None
