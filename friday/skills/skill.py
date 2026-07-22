from typing import Protocol, List, Dict, Any
from friday.skills.skill_metadata import SkillMetadata
from friday.skills.skill_permissions import SkillPermissions
from friday.skills.skill_capability import SkillCapability
from friday.skills.skill_context import SkillContext
from friday.skills.skill_result import SkillResult

class Skill(Protocol):
    """Abstract interface defining the execution protocol for Friday Skills."""
    metadata: SkillMetadata
    permissions: SkillPermissions
    capabilities: List[SkillCapability]

    async def initialize(self, context: SkillContext) -> None:
        ...

    async def start(self) -> None:
        ...

    async def execute(self, capability_name: str, params: Dict[str, Any]) -> SkillResult:
        ...

    async def pause(self) -> None:
        ...

    async def resume(self) -> None:
        ...

    async def stop(self) -> None:
        ...

    async def health_check(self) -> bool:
        ...
