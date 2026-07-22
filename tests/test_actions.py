import os
import shutil
import tempfile
import pytest
from unittest.mock import MagicMock, AsyncMock

from friday.actions.action_models import ActionRequest, ActionType
from friday.actions.action_manager import ActionManager
from friday.actions.action_validator import ActionValidator

@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)

@pytest.mark.asyncio
async def test_action_manager_lifecycle():
    manager = ActionManager()
    manager.initialize()
    await manager.shutdown()
    assert True

@pytest.mark.asyncio
async def test_mouse_actions():
    manager = ActionManager()
    manager.initialize()
    
    # Mock PyAutoGUI actions
    manager.executor.adapter.mouse_move = MagicMock()
    manager.executor.adapter.mouse_click = MagicMock()
    
    req_move = ActionRequest(action_type=ActionType.MOUSE, command="move", arguments={"x": 100, "y": 200})
    res_move = await manager.execute_action(req_move)
    assert res_move.success is True
    manager.executor.adapter.mouse_move.assert_called_once_with(100, 200)

    req_click = ActionRequest(action_type=ActionType.MOUSE, command="click", arguments={"x": 50, "y": 50})
    res_click = await manager.execute_action(req_click)
    assert res_click.success is True
    manager.executor.adapter.mouse_click.assert_called_once_with(50, 50)
    
    await manager.shutdown()

@pytest.mark.asyncio
async def test_keyboard_actions():
    manager = ActionManager()
    manager.initialize()
    
    manager.executor.adapter.keyboard_type = MagicMock()
    
    req = ActionRequest(action_type=ActionType.KEYBOARD, command="type", arguments={"text": "Hello"})
    res = await manager.execute_action(req)
    assert res.success is True
    manager.executor.adapter.keyboard_type.assert_called_once_with("Hello")
    
    await manager.shutdown()

@pytest.mark.asyncio
async def test_filesystem_actions(temp_dir):
    manager = ActionManager()
    mock_security = AsyncMock()
    mock_security.authorize_action.return_value = True
    manager.permissions.security_manager = mock_security
    manager.initialize()
    
    test_file = os.path.join(temp_dir, "test.txt")
    
    # Create file action
    req_create = ActionRequest(
        action_type=ActionType.FILESYSTEM,
        command="create",
        arguments={"path": test_file, "content": "Action test content"}
    )
    res_create = await manager.execute_action(req_create)
    assert res_create.success is True
    assert os.path.exists(test_file)
    
    # Read file action
    req_read = ActionRequest(
        action_type=ActionType.FILESYSTEM,
        command="read",
        arguments={"path": test_file}
    )
    res_read = await manager.execute_action(req_read)
    assert res_read.success is True
    assert res_read.output == "Action test content"
    
    # Delete file action
    req_delete = ActionRequest(
        action_type=ActionType.FILESYSTEM,
        command="delete",
        arguments={"path": test_file}
    )
    res_delete = await manager.execute_action(req_delete)
    assert res_delete.success is True
    assert not os.path.exists(test_file)
    
    await manager.shutdown()

@pytest.mark.asyncio
async def test_terminal_actions():
    manager = ActionManager()
    manager.initialize()
    
    # Execute terminal command
    req = ActionRequest(
        action_type=ActionType.TERMINAL,
        command="run",
        arguments={"cmd": "echo 'Friday Action'"}
    )
    res = await manager.execute_action(req)
    # Since terminal run is sensitive, we mock the PermissionManager authorization
    # Or register a mock SecurityManager to authorize it
    mock_security = AsyncMock()
    mock_security.authorize_action.return_value = True
    manager.permissions.security_manager = mock_security
    
    res = await manager.execute_action(req)
    assert res.success is True
    assert "Friday Action" in res.output["stdout"]
    
    await manager.shutdown()

def test_action_validator():
    validator = ActionValidator()
    
    req_valid = ActionRequest(action_type=ActionType.MOUSE, command="move", arguments={"x": 100, "y": 200})
    assert validator.validate(req_valid) is True
    
    req_invalid_coords = ActionRequest(action_type=ActionType.MOUSE, command="move", arguments={"x": -10, "y": 200})
    with pytest.raises(ValueError, match="must be non-negative"):
        validator.validate(req_invalid_coords)
        
    req_invalid_path = ActionRequest(action_type=ActionType.FILESYSTEM, command="create", arguments={"path": "../stray_file.txt"})
    with pytest.raises(ValueError, match="Directory traversal outside workspace is forbidden"):
        validator.validate(req_invalid_path)
