from __future__ import annotations

import logging
from typing import List, Any
from friday.automation.workflow_models import WorkflowStep
from friday.actions.action_models import ActionRequest, ActionType

logger = logging.getLogger("friday-agent")

class RollbackManager:
    def __init__(self, action_manager: Any):
        self.action_manager = action_manager

    async def rollback_step(self, step: WorkflowStep) -> bool:
        """Attempts to undo/rollback a completed workflow step if it defines rollback parameters."""
        if not step.rollback_command:
            logger.info(f"[RollbackManager] Step {step.step_id} does not define a rollback command. Skipping.")
            return True
            
        logger.warning(f"[RollbackManager] Triggering rollback command '{step.rollback_command}' for step: {step.step_id}")
        try:
            req = ActionRequest(
                action_type=ActionType(step.action_type),
                command=step.rollback_command,
                arguments=step.rollback_arguments
            )
            res = await self.action_manager.execute_action(req)
            return res.success
        except Exception as e:
            logger.error(f"[RollbackManager] Rollback execution failed for step {step.step_id}: {e}")
            return False
            
    async def rollback_workflow(self, executed_steps: List[WorkflowStep]) -> None:
        """Rolls back all successfully executed steps in reverse order."""
        for step in reversed(executed_steps):
            await self.rollback_step(step)
