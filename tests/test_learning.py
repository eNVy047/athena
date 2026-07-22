import pytest
from unittest.mock import MagicMock, AsyncMock

from friday.learning.learning_manager import LearningManager
from friday.learning.experience_models import Experience
from friday.learning.learning_context import LearningContext
from friday.learning.learning_result import LearningResult
from friday.events.event_bus import EventBus
from friday.providers.llm.base import LlmProvider
from friday.memory.memory_manager import MemoryManager
from friday.world.world_manager import WorldManager
from friday.core.kernel.kernel import FridayKernel

class MockLlmProvider(LlmProvider):
    def __init__(self): pass
    async def initialize(self): pass
    async def connect(self): pass
    async def disconnect(self): pass
    async def health_check(self): return True
    async def generate(self, prompt: str, **kwargs) -> str:
        return "Lesson: Mock learning works."
    async def chat(self, messages: list, **kwargs) -> str:
        return "Lesson: Mock learning works."
    async def chat_stream(self, messages: list, **kwargs):
        yield "Lesson: Mock learning works."

class MockMemoryManager(MemoryManager):
    def __init__(self): pass
    async def add_memory(self, text, metadata=None): pass

@pytest.mark.asyncio
async def test_learning_cycle():
    llm = MockLlmProvider()
    mem = MockMemoryManager()
    
    kernel = FridayKernel()
    bus = EventBus()
    world = WorldManager(kernel, bus)
    
    learning_manager = LearningManager(llm, mem, world, bus)
    
    exp = Experience(id="test_exp", type="workflow", trigger="user_command", success=True)
    await learning_manager.log_experience(exp)
    
    context = LearningContext(session_id="test_session", trigger_source="manual")
    result = await learning_manager.run_reflection_cycle(context)
    
    assert result.success is True
    # In Mock implementations, these return predefined arrays
    assert result.patterns_detected >= 0
    assert result.preferences_updated >= 0
    
    # We should have insights from the mocked analyzers
    assert len(result.insights_generated) > 0
    assert any("Mock learning works." in i or "Lesson" in i or "Pattern" in i or "Success Insight" in i for i in result.insights_generated)
