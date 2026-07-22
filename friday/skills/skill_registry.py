from typing import Dict, List, Optional
from friday.skills.skill import Skill
from friday.skills.skill_capability import SkillCapability

class SkillRegistry:
    """Central repository storing loaded Skills and mapping their exposed Capabilities."""
    def __init__(self):
        self._skills: Dict[str, Skill] = {}
        self._capability_map: Dict[str, str] = {}  # Capability Name -> Skill Name

    def register(self, skill: Skill) -> None:
        self._skills[skill.metadata.name] = skill
        for cap in skill.capabilities:
            self._capability_map[cap.name] = skill.metadata.name

    def unregister(self, skill_name: str) -> None:
        if skill_name in self._skills:
            skill = self._skills[skill_name]
            for cap in skill.capabilities:
                if cap.name in self._capability_map:
                    del self._capability_map[cap.name]
            del self._skills[skill_name]

    def get_skill(self, name: str) -> Optional[Skill]:
        return self._skills.get(name)

    def find_skill_by_capability(self, capability_name: str) -> Optional[Skill]:
        skill_name = self._capability_map.get(capability_name)
        if skill_name:
            return self.get_skill(skill_name)
        return None

    def list_all_skills(self) -> List[Skill]:
        return list(self._skills.values())
