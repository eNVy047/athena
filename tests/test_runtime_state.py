import pytest
from friday.kernel.runtime_state import RuntimeState

def test_runtime_state_defaults():
    state = RuntimeState()
    assert state.health_status == "healthy"
    assert state.active_conversation_id is None
    
    state.active_conversation_id = "conv123"
    assert state.active_conversation_id == "conv123"
