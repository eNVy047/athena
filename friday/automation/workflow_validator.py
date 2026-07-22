from __future__ import annotations

from friday.automation.workflow_models import Workflow

class WorkflowValidator:
    def validate_workflow(self, workflow: Workflow) -> bool:
        """Validates that a workflow schema is well-formed."""
        if not workflow.workflow_id:
            raise ValueError("Workflow ID is missing.")
        if not workflow.steps:
            raise ValueError("Workflow must contain at least one step.")
        
        seen_steps = set()
        for step in workflow.steps:
            if not step.step_id:
                raise ValueError("Step ID is missing.")
            if step.step_id in seen_steps:
                raise ValueError(f"Duplicate step ID found: {step.step_id}")
            seen_steps.add(step.step_id)
            
            if not step.action_type or not step.command:
                raise ValueError(f"Step {step.step_id} must have a valid action_type and command.")
                
        return True
