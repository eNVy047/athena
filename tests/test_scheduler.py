import pytest
import asyncio
from datetime import datetime, timedelta
from friday.scheduler.queue import PriorityTaskQueue
from friday.scheduler.scheduler import TaskScheduler

@pytest.mark.asyncio
async def test_scheduler_task_triggering():
    queue = PriorityTaskQueue()
    scheduler = TaskScheduler(queue=queue)
    
    execution_record = []
    
    def test_callback():
        execution_record.append("run")
        
    scheduler.register_task_callback("task1", test_callback)
    
    # 1. Delayed task triggering immediately
    scheduler.add_delayed_task("task1", run_at=datetime.utcnow() - timedelta(seconds=1))
    scheduler.start()
    
    await asyncio.sleep(1.2)
    scheduler.stop()
    
    assert len(execution_record) == 1
    assert execution_record[0] == "run"

@pytest.mark.asyncio
async def test_scheduler_e2e_agent():
    from friday.kernel.kernel import FridayKernel
    from friday.kernel.runtime import FridayAgent
    from pathlib import Path
    import shutil
    
    storage_root = Path(__file__).parent.parent / "friday" / "prompts" / "temp_scheduler_agent_test"
    kernel = FridayKernel(storage_root=storage_root)
    kernel.bootstrap()
    agent = FridayAgent(kernel=kernel)
    
    res = await agent.process_input("Create reminder for tomorrow")
    assert "task created" in res.lower()
    
    kernel.shutdown()
    shutil.rmtree(storage_root, ignore_errors=True)

