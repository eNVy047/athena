from __future__ import annotations

import logging
from typing import Dict, Any, Optional
from friday.automation.workflow_models import Workflow
from friday.automation.workflow_result import WorkflowResult
from friday.automation.workflow_state import WorkflowState
from friday.automation.workflow_executor import WorkflowExecutor
from friday.automation.workflow_scheduler import WorkflowScheduler
from friday.automation.checkpoint_manager import CheckpointManager
from friday.automation.workflow_permissions import WorkflowPermissionManager
from friday.automation.workflow_validator import WorkflowValidator
from friday.automation.workflow_history import WorkflowHistory

logger = logging.getLogger("friday-agent")

class WorkflowManager:
    def __init__(self, action_manager: Any, security_manager: Optional[Any] = None, event_bus: Optional[Any] = None, memory_manager: Optional[Any] = None):
        self.action_manager = action_manager
        self.checkpoint = CheckpointManager()
        self.permissions = WorkflowPermissionManager(security_manager)
        self.validator = WorkflowValidator()
        self.history = WorkflowHistory(memory_manager)
        self.scheduler = WorkflowScheduler()
        self.executor = WorkflowExecutor(action_manager, self.checkpoint, event_bus)
        
        self.workflows: Dict[str, Workflow] = {}
        self.running_states: Dict[str, WorkflowState] = {}

    def register_workflow(self, workflow: Workflow) -> None:
        self.validator.validate_workflow(workflow)
        self.workflows[workflow.workflow_id] = workflow
        logger.info(f"[WorkflowManager] Registered workflow: {workflow.workflow_id}")

    async def execute_workflow(self, workflow_id: str) -> WorkflowResult:
        """Executes registered workflow by validating permissions and invoking executor."""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not registered.")

        allowed = await self.permissions.check_workflow_permissions(workflow)
        if not allowed:
            raise PermissionError(f"Workflow {workflow_id} denied execution permissions.")

        # Check for checkpoint recovery
        state = self.checkpoint.load_checkpoint(workflow_id)
        if state:
            logger.info(f"[WorkflowManager] Recovering workflow {workflow_id} from step index {state.current_step_index}")
        
        res = await self.executor.execute_workflow(workflow, state)
        await self.history.record_run(res)
        return res

    def shutdown(self) -> None:
        self.scheduler.stop()
