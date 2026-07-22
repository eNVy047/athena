from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any

SKILL_LOADED = "skill.loaded"
SKILL_STARTED = "skill.started"
SKILL_STOPPED = "skill.stopped"
SKILL_FAILED = "skill.failed"
SKILL_PAUSED = "skill.paused"
SKILL_RESUMED = "skill.resumed"
SKILL_UPDATED = "skill.updated"

@dataclass
class SkillEvent:
    """Event data block indicating changes in a Skill lifecycle status."""
    name: str
    skill_name: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
