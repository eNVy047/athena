import pytest
from unittest.mock import AsyncMock

from friday.agent.agent_session import AgentSession
from friday.agent.request_context import RequestContext
from friday.agent.agent_manager import AgentManager

@pytest.mark.asyncio
async def test_agent_orchestrator_pipeline():
    # Setup mock dependencies
    mock_memory = AsyncMock()
    mock_memory.sync_turn.return_value = "Memory Context Mock"
    mock_memory.store_memory.return_value = None
    
    mock_sec = AsyncMock()
    mock_sec.authorize_action.return_value = True

    # Instantiate Agent Manager
    manager = AgentManager(
        security_manager=mock_sec,
        memory_manager=mock_memory
    )
    
    agent = manager.get_or_create_agent("friday_primary")
    
    session = AgentSession(conversation_id="conv_123", user_id="user_1")
    request = RequestContext(payload={"user_id": "user_1", "query": "hello world"})
    
    result = await agent.handle_request(session, request)
    
    # Assert successful execution
    assert result.success is True
    assert "Processed request matching route" in result.output
    
    # Verify memory integration calls
    mock_memory.sync_turn.assert_called_once_with("hello world")
    mock_memory.store_memory.assert_called_once()
    
    # Verify conversational history tracking
    history = agent.conversations.get_history("conv_123")
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
