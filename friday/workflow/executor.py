import asyncio
from typing import Any, Callable, Coroutine
from friday.workflow.state import WorkflowStep

class StepExecutor:
    async def execute_step(self, step: WorkflowStep, task_coro: Coroutine[Any, Any, Any], timeout: float = 60.0) -> Any:
        step.status = "running"
        try:
            # Execute step task with custom timeout
            res = await asyncio.wait_for(task_coro, timeout=timeout)
            step.status = "completed"
            step.result = res
            return res
        except asyncio.TimeoutError:
            step.status = "failed"
            step.error = f"Step timed out after {timeout}s."
            raise TimeoutError(step.error)
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            raise e
