import time
import asyncio
from typing import Dict, Any, Callable, Coroutine
from friday.core.cognition.models import Plan, TaskStatus, ExecutionResult
from friday.events.event_bus import EventBus

class Executor:
    """Orchestrates step execution, timeouts, retries, and publishes status events."""
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._action_handlers: Dict[str, Callable[[Dict[str, Any]], Coroutine[Any, Any, Any]]] = {}

    def register_action_handler(
        self, action_name: str, handler: Callable[[Dict[str, Any]], Coroutine[Any, Any, Any]]
    ) -> None:
        self._action_handlers[action_name] = handler

    async def execute_plan(self, plan: Plan) -> bool:
        # Resolve dependencies topologically
        completed_tasks: Dict[str, TaskStatus] = {}
        
        while len(completed_tasks) < len(plan.tasks):
            runnable_tasks = [
                task for tid, task in plan.tasks.items()
                if task.id not in completed_tasks and all(dep in completed_tasks and completed_tasks[dep] == TaskStatus.COMPLETED for dep in task.dependencies)
            ]
            
            if not runnable_tasks:
                # Deadlock or cyclic dependencies
                break

            for task in runnable_tasks:
                task.status = TaskStatus.RUNNING
                await self.event_bus.publish("task.started", {"task_id": task.id, "plan_id": plan.id})
                
                task_success = True
                for step in task.steps:
                    handler = self._action_handlers.get(step.action_name)
                    if not handler:
                        # Mark failed if no handler found
                        task.results.append(ExecutionResult(
                            step_id=step.id, success=False, error=f"No action handler registered for: {step.action_name}"
                        ))
                        task_success = False
                        break

                    start_time = time.time()
                    try:
                        # Wrap execution in timeout
                        output = await asyncio.wait_for(handler(step.parameters), timeout=step.timeout)
                        task.results.append(ExecutionResult(
                            step_id=step.id, success=True, output=output, execution_time=time.time() - start_time
                        ))
                    except Exception as e:
                        task.results.append(ExecutionResult(
                            step_id=step.id, success=False, error=str(e), execution_time=time.time() - start_time
                        ))
                        task_success = False
                        break

                if task_success:
                    task.status = TaskStatus.COMPLETED
                else:
                    task.status = TaskStatus.FAILED
                
                completed_tasks[task.id] = task.status
                await self.event_bus.publish("task.finished", {"task_id": task.id, "status": task.status.value})
                
                if task.status == TaskStatus.FAILED:
                    return False
                    
        return all(t.status == TaskStatus.COMPLETED for t in plan.tasks.values())
