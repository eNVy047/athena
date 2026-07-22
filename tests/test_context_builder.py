import pytest
from datetime import datetime
from friday.domain.context import ExecutionContext, ChatMessage
from friday.domain.pal import PlatformCapabilities
from friday.application.services.context_builder import ContextBuilder

def test_context_builder_assembly():
    caps = PlatformCapabilities(has_browser=True, has_terminal=True, has_audio_input=True)
    builder = ContextBuilder(capabilities=caps)
    
    exec_ctx = ExecutionContext(
        session_id="session123",
        user_id="user456",
        chat_history=[
            ChatMessage(role="user", content="Hello Friday"),
            ChatMessage(role="assistant", content="Hello Narayan")
        ]
    )
    
    memories = ["Narayan prefers Python.", "Workspace path is set to jarvis/."]
    workspace_details = "File count: 12"
    planner_state = {"goal": "Scan registry", "current_step": "Step 1: Check PIDs"}
    
    structured_context = builder.build_structured_context(
        exec_context=exec_ctx,
        memories=memories,
        planner_state=planner_state,
        workspace_details=workspace_details
    )
    
    assert "### PLATFORM CAPABILITIES" in structured_context
    assert "Browser Available: True" in structured_context
    assert "Verify setup" not in structured_context
    assert "Narayan prefers Python." in structured_context
    assert "Scan registry" in structured_context
    assert "File count: 12" in structured_context
    assert "[USER]: Hello Friday" in structured_context
