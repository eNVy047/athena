import pytest
from typing import Dict, Any, List
from friday.core.kernel.kernel import FridayKernel
from friday.events.event_bus import EventBus
from friday.skills.skill import Skill
from friday.skills.skill_metadata import SkillMetadata
from friday.skills.skill_permissions import SkillPermissions
from friday.skills.skill_capability import SkillCapability
from friday.skills.skill_context import SkillContext
from friday.skills.skill_result import SkillResult
from friday.skills.skill_manager import SkillManager

class MockBrowserSkill:
    """Mock implementation conforming to the Skill protocol for testing."""
    def __init__(self):
        self.metadata = SkillMetadata(
            name="BrowserSkill",
            description="Allows web browsing capability",
            version="1.0.0",
            dependencies=[]
        )
        self.permissions = SkillPermissions(execute=True)
        self.capabilities = [SkillCapability(name="Web Browsing", description="Fetch website text")]
        self.initialized = False
        self.started = False

    async def initialize(self, context: SkillContext) -> None:
        self.initialized = True

    async def start(self) -> None:
        self.started = True

    async def execute(self, capability_name: str, params: Dict[str, Any]) -> SkillResult:
        if capability_name == "Web Browsing":
            return SkillResult(success=True, data="parsed_html_content")
        return SkillResult(success=False, error="Unknown capability")

    async def pause(self) -> None:
        pass

    async def resume(self) -> None:
        pass

    async def stop(self) -> None:
        self.started = False

    async def health_check(self) -> bool:
        return True

@pytest.mark.asyncio
async def test_skill_manager_lifecycle_and_resolution():
    kernel = FridayKernel()
    bus = EventBus()
    manager = SkillManager(kernel, bus)
    
    skill = MockBrowserSkill()
    await manager.load_and_initialize_skill(skill)
    
    # Assert initialized state
    assert skill.initialized is True
    assert manager.registry.get_skill("BrowserSkill") is not None
    
    # Assert start lifecycle
    await manager.start_skill("BrowserSkill")
    assert skill.started is True
    assert manager.is_active("BrowserSkill") is True
    
    # Assert resolution by capability
    resolved = manager.registry.find_skill_by_capability("Web Browsing")
    assert resolved is not None
    assert resolved.metadata.name == "BrowserSkill"
    
    # Execute capability call
    res = await resolved.execute("Web Browsing", {})
    assert res.success is True
    assert res.data == "parsed_html_content"
    
    # Stop lifecycle
    await manager.stop_skill("BrowserSkill")
    assert skill.started is False
    assert manager.is_active("BrowserSkill") is False

@pytest.mark.asyncio
async def test_skill_dependencies_resolution():
    kernel = FridayKernel()
    bus = EventBus()
    manager = SkillManager(kernel, bus)
    
    dependent_skill = MockBrowserSkill()
    dependent_skill.metadata = SkillMetadata(
        name="DependentSkill",
        description="Requires BrowserSkill",
        version="1.0.0",
        dependencies=["BrowserSkill"]
    )
    
    # Loading must fail because BrowserSkill is not loaded yet
    with pytest.raises(ValueError):
        await manager.load_and_initialize_skill(dependent_skill)
