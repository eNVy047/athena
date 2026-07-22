from typing import List
from friday.workflow.state import WorkflowState, WorkflowStep

class WorkflowScheduler:
    @staticmethod
    def get_next_runnable_steps(state: WorkflowState) -> List[WorkflowStep]:
        """Resolves which steps are currently runnable based on statuses."""
        if state.status in ["completed", "failed", "paused"]:
            return []
            
        runnable = []
        for step in state.steps:
            if step.status == "pending":
                runnable.append(step)
        return runnable
