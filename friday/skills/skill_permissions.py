from dataclasses import dataclass

@dataclass
class SkillPermissions:
    """Security authorization settings defining what actions a Skill can perform."""
    read: bool = True
    write: bool = False
    execute: bool = False
    sensitive: bool = False
    requires_approval: bool = False
    sandbox: bool = True
