import pytest
from pathlib import Path
from friday.workspace.manager import WorkspaceManager

def test_workspace_project_and_temp_cleanup():
    base_dir = Path(__file__).parent.parent / "friday" / "prompts" / "temp_workspace"
    manager = WorkspaceManager(workspace_root=base_dir)
    
    # 1. Create project
    project = manager.create_project("protocol_shield", "Stark suit diagnostics")
    assert project.root_path.exists()
    assert manager.get_project("protocol_shield") == project
    
    # 2. Temp workspace spawning
    temp_path = manager.create_temp_workspace("session_85")
    assert temp_path.exists()
    
    # 3. Cleanup check
    manager.cleanup_temp_workspaces()
    assert not temp_path.exists()
    
    # Cleanup base
    import shutil
    shutil.rmtree(base_dir, ignore_errors=True)

@pytest.mark.asyncio
async def test_workspace_e2e_agent():
    from friday.kernel.kernel import FridayKernel
    from friday.kernel.runtime import FridayAgent
    import shutil
    
    storage_root = Path(__file__).parent.parent / "friday" / "prompts" / "temp_workspace_agent_test"
    kernel = FridayKernel(storage_root=storage_root)
    kernel.bootstrap()
    agent = FridayAgent(kernel=kernel)
    
    res = await agent.process_input("Create hello.py")
    assert "created in workspace" in res
    
    kernel.shutdown()
    shutil.rmtree(storage_root, ignore_errors=True)

