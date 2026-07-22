import pytest
import asyncio
from pathlib import Path
from friday.workflow.state import WorkflowState, WorkflowStep
from friday.workflow.checkpoint import WorkflowCheckpointManager
from friday.workflow.executor import StepExecutor
from friday.workflow.engine import WorkflowEngine

@pytest.mark.asyncio
async def test_workflow_engine_execution():
    storage_dir = Path(__file__).parent.parent / "friday" / "prompts" / "temp_checkpoints"
    checkpoint_mgr = WorkflowCheckpointManager(storage_dir=storage_dir)
    executor = StepExecutor()
    engine = WorkflowEngine(checkpoint_manager=checkpoint_mgr, step_executor=executor)
    
    state = WorkflowState(
        workflow_id="wf_123",
        name="Setup Friday Pipeline",
        steps=[
            WorkflowStep(step_id="step1", name="Verify local storage"),
            WorkflowStep(step_id="step2", name="Load capability graph")
        ]
    )
    
    async def mock_task1():
        await asyncio.sleep(0.01)
        return "Storage OK"
        
    async def mock_task2():
        await asyncio.sleep(0.01)
        return "Caps OK"
        
    mappings = {
        "step1": mock_task1,
        "step2": mock_task2
    }
    
    res_state = await engine.run_workflow(state, mappings)
    
    assert res_state.status == "completed"
    assert res_state.steps[0].result == "Storage OK"
    assert res_state.steps[1].result == "Caps OK"
    
    # Verify checkpoint persisted
    loaded = checkpoint_mgr.load_checkpoint("wf_123")
    assert loaded is not None
    assert loaded.status == "completed"
    
    # Cleanup
    import shutil
    shutil.rmtree(storage_dir, ignore_errors=True)

@pytest.mark.asyncio
async def test_workflow_e2e_agent(monkeypatch):
    from friday.kernel.kernel import FridayKernel
    from friday.kernel.runtime import FridayAgent
    import shutil
    import subprocess
    monkeypatch.setattr(shutil, "which", lambda cmd: "/usr/bin/chrome" if "chrome" in cmd or "chromium" in cmd or "python" in cmd or "firefox" in cmd or "safari" in cmd else None)
    def mock_subprocess_run(*args, **kwargs):
        class MockCompletedProcess:
            returncode = 1
            stdout = ""
            stderr = ""
        return MockCompletedProcess()
    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)
    
    storage_root = Path(__file__).parent.parent / "friday" / "prompts" / "temp_workflow_agent_test"
    kernel = FridayKernel(storage_root=storage_root)
    kernel.bootstrap()
    agent = FridayAgent(kernel=kernel)
    
    res = await agent.process_input("Open Chrome, search FastMCP, summarize results, save summary, remember summary location")
    assert "dialog" in res.lower() or "dialogue" in res.lower()
    
    kernel.shutdown()
    shutil.rmtree(storage_root, ignore_errors=True)

