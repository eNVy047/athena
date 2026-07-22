from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class SkillResult:
    """Standardized response container for Skill capability execution."""
    success: bool
    data: Any = None
    error: Optional[str] = None
