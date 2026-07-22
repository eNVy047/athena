from dataclasses import dataclass, field
from typing import List

@dataclass
class SkillCapability:
    """Represents a specific feature or function provided by a Friday Skill."""
    name: str
    description: str
    parameters_schema: dict = field(default_factory=dict)
