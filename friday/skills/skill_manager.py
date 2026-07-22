import logging
from typing import Dict, Any, List, Optional
from friday.skills.skill import Skill
from friday.skills.skill_registry import SkillRegistry
from friday.skills.skill_loader import SkillLoader
from friday.skills.skill_context import SkillContext
from friday.skills.skill_events import (
    SKILL_LOADED, SKILL_STARTED, SKILL_STOPPED, SKILL_FAILED, SKILL_PAUSED, SKILL_RESUMED
)
from friday.core.kernel.kernel import FridayKernel
from friday.events.event_bus import EventBus

logger = logging.getLogger(__name__)

class SkillManager:
    """Orchestrates loading, unloading, dependency verification, and lifecycle states of Friday Skills."""
    def __init__(self, kernel: FridayKernel, event_bus: EventBus):
        self.kernel = kernel
        self.event_bus = event_bus
        self.registry = SkillRegistry()
        self.loader = SkillLoader()
        self._active_states: Dict[str, str] = {}  # Skill Name -> Status string

        # Register services
        self.kernel.services.register(SkillManager, self)
        self.kernel.services.register(SkillRegistry, self.registry)

    async def load_and_initialize_skill(self, skill: Skill) -> None:
        name = skill.metadata.name
        
        # Verify dependencies
        for dep in skill.metadata.dependencies:
            if not self.registry.get_skill(dep):
                raise ValueError(f"Dependency unresolved: {name} requires {dep}")
        
        context = SkillContext(self.kernel, self.event_bus, f"skill.{name}")
        await skill.initialize(context)
        
        self.registry.register(skill)
        self._active_states[name] = "initialized"
        await self.event_bus.publish(SKILL_LOADED, {"skill_name": name})
        logger.info(f"Skill loaded and initialized: {name}")

    async def start_skill(self, name: str) -> None:
        skill = self.registry.get_skill(name)
        if skill and self._active_states.get(name) == "initialized":
            await skill.start()
            self._active_states[name] = "started"
            await self.event_bus.publish(SKILL_STARTED, {"skill_name": name})
            logger.info(f"Skill started: {name}")

    async def stop_skill(self, name: str) -> None:
        skill = self.registry.get_skill(name)
        if skill and self._active_states.get(name) == "started":
            await skill.stop()
            self._active_states[name] = "stopped"
            await self.event_bus.publish(SKILL_STOPPED, {"skill_name": name})
            logger.info(f"Skill stopped: {name}")

    def is_active(self, name: str) -> bool:
        return self._active_states.get(name) == "started"
