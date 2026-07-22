import asyncio
from typing import Dict, Any, List, Callable
from friday.workflow.state import WorkflowState, WorkflowStep
from friday.workflow.checkpoint import WorkflowCheckpointManager
from friday.workflow.scheduler import WorkflowScheduler
from friday.workflow.executor import StepExecutor

class WorkflowEngine:
    def __init__(self, checkpoint_manager: WorkflowCheckpointManager, step_executor: StepExecutor):
        self.checkpoint_manager = checkpoint_manager
        self.step_executor = step_executor
        self.scheduler = WorkflowScheduler()

    async def run_workflow(self, state: WorkflowState, task_mappings: Dict[str, Callable[[], Any]]) -> WorkflowState:
        state.status = "running"
        self.checkpoint_manager.save_checkpoint(state)

        while True:
            runnable_steps = self.scheduler.get_next_runnable_steps(state)
            if not runnable_steps:
                break

            # Execute runnables in parallel (using asyncio.gather)
            tasks = []
            for step in runnable_steps:
                state.current_step_id = step.step_id
                coro = task_mappings[step.step_id]()
                tasks.append(self.step_executor.execute_step(step, coro))

            try:
                await asyncio.gather(*tasks)
            except Exception:
                state.status = "failed"
                self.checkpoint_manager.save_checkpoint(state)
                return state

            self.checkpoint_manager.save_checkpoint(state)

        # Check if all steps succeeded
        if all(step.status == "completed" for step in state.steps):
            state.status = "completed"
        else:
            state.status = "failed"
            
        self.checkpoint_manager.save_checkpoint(state)
        return state
