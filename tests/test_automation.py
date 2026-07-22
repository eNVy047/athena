import os
import shutil
import tempfile
import asyncio
import pytest
from unittest.mock import AsyncMock

from friday.automation.workflow_models import Workflow, WorkflowStep
from friday.automation.automation_manager import AutomationManager
from friday.actions.action_manager import ActionManager
from friday.events.event_bus import EventBus
from friday.events.event_types import Event

@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)

@pytest.mark.asyncio
async def test_sequential_workflow_execution(temp_dir):
    action_manager = ActionManager()
    action_manager.initialize()
    
    # Mock SecurityManager to authorize everything
    mock_sec = AsyncMock()
    mock_sec.authorize_action.return_value = True
    action_manager.permissions.security_manager = mock_sec
    
    # Create temp files to modify in workflow
    file1 = os.path.join(temp_dir, "step1.txt")
    file2 = os.path.join(temp_dir, "step2.txt")

    workflow = Workflow(
        workflow_id="seq_flow",
        name="Sequential Workflow Test",
        steps=[
            WorkflowStep(
                step_id="s1",
                action_type="filesystem",
                command="create",
                arguments={"path": file1, "content": "hello"}
            ),
            WorkflowStep(
                step_id="s2",
                action_type="filesystem",
                command="create",
                arguments={"path": file2, "content": "world"}
            )
        ]
    )

    manager = AutomationManager(action_manager, security_manager=mock_sec)
    manager.initialize()
    manager.workflow_manager.register_workflow(workflow)
    
    res = await manager.workflow_manager.execute_workflow("seq_flow")
    assert res.success is True
    assert len(res.step_results) == 2
    assert os.path.exists(file1)
    assert os.path.exists(file2)
    
    manager.shutdown()
    await action_manager.shutdown()

@pytest.mark.asyncio
async def test_conditional_workflow_execution(temp_dir):
    action_manager = ActionManager()
    action_manager.initialize()
    
    mock_sec = AsyncMock()
    mock_sec.authorize_action.return_value = True
    action_manager.permissions.security_manager = mock_sec
    
    file_to_skip = os.path.join(temp_dir, "skip.txt")

    workflow = Workflow(
        workflow_id="cond_flow",
        name="Conditional Workflow Test",
        steps=[
            WorkflowStep(
                step_id="s1",
                action_type="filesystem",
                command="create",
                arguments={"path": file_to_skip, "content": "skipped?"},
                condition="False" # Should evaluate to False and skip
            )
        ]
    )

    manager = AutomationManager(action_manager, security_manager=mock_sec)
    manager.initialize()
    manager.workflow_manager.register_workflow(workflow)
    
    res = await manager.workflow_manager.execute_workflow("cond_flow")
    assert res.success is True
    assert len(res.step_results) == 0  # Skipped step
    assert not os.path.exists(file_to_skip)
    
    manager.shutdown()
    await action_manager.shutdown()

@pytest.mark.asyncio
async def test_workflow_trigger_engine():
    event_bus = EventBus()
    action_manager = ActionManager()
    action_manager.initialize()
    
    manager = AutomationManager(action_manager, event_bus=event_bus)
    manager.initialize()

    # Define a callback mock to fire when event triggered
    trigger_fired = asyncio.Event()
    async def trigger_cb(event):
        trigger_fired.set()

    manager.trigger_engine.register_trigger("test.custom_event", trigger_cb)
    
    # Fire event via Event Bus
    await event_bus.publish("test.custom_event", Event(event_type="test.custom_event", data={}, timestamp=asyncio.get_event_loop().time()))
    
    # Wait for trigger callback execution
    await asyncio.wait_for(trigger_fired.wait(), timeout=2.0)
    assert trigger_fired.is_set()
    
    manager.shutdown()
    await action_manager.shutdown()
