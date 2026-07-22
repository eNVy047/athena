import pytest
import asyncio
from friday.core.tasks import BackgroundTaskManager

@pytest.mark.asyncio
async def test_background_task_manager():
    mgr = BackgroundTaskManager()
    task_run = False
    
    async def mock_coro():
        nonlocal task_run
        await asyncio.sleep(0.01)
        task_run = True
        
    task = mgr.submit(mock_coro())
    await asyncio.sleep(0.05)
    
    assert task_run
    await mgr.shutdown()
