from dataclasses import dataclass, field
from typing import List

@dataclass
class SkillMetadata:
    """Attributes defining a Friday Skill's identification, versioning, and dependencies."""
    name: str
    description: str
    version: str
    dependencies: List[str] = field(default_factory=list)
