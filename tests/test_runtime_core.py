import pytest
import asyncio
from datetime import datetime
from friday.core.kernel.kernel import FridayKernel
from friday.events.event_bus import EventBus
from friday.core.cognition.models import Plan, Task, ExecutionStep, TaskStatus
from friday.runtime.runtime_manager import RuntimeManager
from friday.runtime.task_queue import TaskQueue
from friday.runtime.retry_manager import RetryManager
from friday.runtime.timeout_manager import TimeoutManager

@pytest.mark.asyncio
async def test_runtime_task_queue_priority():
    queue = TaskQueue()
    task1 = Task(id="t1", name="Task 1", steps=[])
    task2 = Task(id="t2", name="Task 2", steps=[])
    
    await queue.enqueue(task1, priority=1)
    await queue.enqueue(task2, priority=10)
    
    first = await queue.dequeue()
    assert first.id == "t2"  # Highest priority first

@pytest.mark.asyncio
async def test_runtime_retry_and_timeout():
    retry_manager = RetryManager()
    timeout_manager = TimeoutManager()
    
    call_count = 0
    async def mock_fail_func(params):
        nonlocal call_count
        call_count += 1
        raise ValueError("Intentional error")

    with pytest.raises(ValueError):
        await retry_manager.execute_with_retry(mock_fail_func, {}, max_retries=2, backoff=0.01)
    
    assert call_count == 3  # Initial + 2 retries

    async def mock_long_func(params):
        await asyncio.sleep(1.0)
        return "done"

    with pytest.raises(asyncio.TimeoutError):
        await timeout_manager.execute_with_timeout(mock_long_func, {}, timeout=0.01)

@pytest.mark.asyncio
async def test_runtime_job_execution_flow():
    kernel = FridayKernel()
    bus = EventBus()
    runtime = RuntimeManager(kernel, bus)
    
    execution_completed = False
    async def mock_handler(params):
        nonlocal execution_completed
        execution_completed = True
        return "report_done"

    runtime.register_action_handler("os.download", mock_handler)
    
    step = ExecutionStep(id="s1", action_name="os.download")
    task = Task(id="t1", name="Download report", steps=[step])
    plan = Plan(id="job_123", goal_id="g123", tasks={"t1": task})
    
    runtime.job_store.store_job("job_123", plan)
    
    success = await runtime.job_executor.execute_job(plan)
    assert success is True
    assert execution_completed is True
    
    progress = runtime.progress_tracker.get_progress("job_123")
    assert progress["status"] == "completed"
    assert progress["progress"] == 100.0

@pytest.mark.asyncio
async def test_runtime_resource_and_health_monitoring():
    kernel = FridayKernel()
    bus = EventBus()
    runtime = RuntimeManager(kernel, bus)
    
    health = runtime.health_monitor.get_health_status()
    assert health["status"] == "healthy"
    assert "cpu_usage" in health
    assert "ram_usage" in health
