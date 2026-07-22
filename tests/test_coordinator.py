import pytest
from friday.multi_agent.orchestration.coordinator import Coordinator
from friday.multi_agent.agent_registry import AgentRegistry
from friday.multi_agent.communication.message_bus import MessageBus
from friday.multi_agent.agent_profile import AgentProfile

@pytest.mark.asyncio
async def test_coordinator_dispatch():
    registry = AgentRegistry()
    bus = MessageBus()
    
    # Register a mock capable agent
    registry.register(AgentProfile(
        agent_id="agent_1", 
        name="Agent 1", 
        description="", 
        capabilities=["test_cap"]
    ))
    
    coordinator = Coordinator(registry, bus)
    
    res = await coordinator.delegate("test objective", ["test_cap"])
    assert res.success is True
    assert "agent_1" in res.message
    
    # Test unavailable capability
    res_fail = await coordinator.delegate("test objective", ["unknown_cap"])
    assert res_fail.success is False
