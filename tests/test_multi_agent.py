import pytest
from friday.multi_agent.multi_agent_manager import MultiAgentManager
from friday.multi_agent.agent_profile import AgentProfile

@pytest.mark.asyncio
async def test_multi_agent_manager():
    manager = MultiAgentManager()
    profile = AgentProfile(agent_id="test_agent", name="Test", description="Test")
    
    manager.registry.register(profile)
    assert manager.registry.get_profile("test_agent").name == "Test"
    
    res = await manager.dispatch_task("Do something")
    assert res.success is True
