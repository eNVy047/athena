from __future__ import annotations

import time
import logging
from typing import Any, List, Optional
from friday.automation.workflow_models import Workflow, WorkflowStep
from friday.automation.workflow_result import WorkflowResult, StepResult
from friday.automation.workflow_state import WorkflowState, ExecutionStatus
from friday.automation.workflow_context import WorkflowContext
from friday.automation.checkpoint_manager import CheckpointManager
from friday.automation.rollback_manager import RollbackManager
from friday.automation.condition_engine import ConditionEngine
from friday.automation.retry_policy import RetryPolicy
from friday.automation.parallel_executor import ParallelExecutor
from friday.automation.workflow_events import WorkflowEvents
from friday.actions.action_models import ActionRequest, ActionType

logger = logging.getLogger("friday-agent")

class WorkflowExecutor:
    def __init__(self, action_manager: Any, checkpoint_manager: CheckpointManager, event_bus: Optional[Any] = None):
        self.action_manager = action_manager
        self.checkpoint = checkpoint_manager
        self.rollback = RollbackManager(action_manager)
        self.condition = ConditionEngine()
        self.retry = RetryPolicy()
        self.parallel = ParallelExecutor()
        self.events = WorkflowEvents(event_bus)

    async def execute_workflow(self, workflow: Workflow, initial_state: Optional[WorkflowState] = None) -> WorkflowResult:
        """Executes a workflow step-by-step with checkpoints, conditional branching, retries, and rollbacks."""
        start_time = time.time()
        await self.events.publish_started(workflow.workflow_id)
        
        state = initial_state or WorkflowState(workflow_id=workflow.workflow_id, status=ExecutionStatus.RUNNING)
        context = WorkflowContext(workflow.workflow_id, state.variables)
        step_results: List[StepResult] = []
        executed_steps: List[WorkflowStep] = []

        try:
            while state.current_step_index < len(workflow.steps):
                step = workflow.steps[state.current_step_index]
                
                # Check condition
                if step.condition:
                    if not self.condition.evaluate(step.condition, context.variables):
                        logger.info(f"[WorkflowExecutor] Condition '{step.condition}' failed. Skipping step {step.step_id}")
                        state.current_step_index += 1
                        continue

                # Run step (with retry support)
                async def run_step_func():
                    req = ActionRequest(
                        action_type=ActionType(step.action_type),
                        command=step.command,
                        arguments=step.arguments
                    )
                    res = await self.action_manager.execute_action(req)
                    if not res.success:
                        raise RuntimeError(res.error or "Action failed")
                    return res.output

                step_start = time.time()
                try:
                    output = await self.retry.execute_with_retry(
                        run_step_func,
                        max_retries=workflow.max_retries,
                        delay_seconds=workflow.retry_delay_seconds
                    )
                    step_results.append(StepResult(
                        step_id=step.step_id,
                        success=True,
                        output=output,
                        execution_time_ms=(time.time() - step_start) * 1000
                    ))
                    executed_steps.append(step)
                    
                    # Store output variable if needed
                    context.set_variable(f"{step.step_id}_output", output)
                except Exception as e:
                    logger.error(f"[WorkflowExecutor] Step {step.step_id} failed: {e}")
                    step_results.append(StepResult(
                        step_id=step.step_id,
                        success=False,
                        error=str(e),
                        execution_time_ms=(time.time() - step_start) * 1000
                    ))
                    
                    # Trigger rollback
                    await self.rollback.rollback_workflow(executed_steps)
                    
                    state.status = ExecutionStatus.FAILED
                    self.checkpoint.clear_checkpoint(workflow.workflow_id)
                    await self.events.publish_completed(workflow.workflow_id, success=False, error=str(e))
                    return WorkflowResult(
                        workflow_id=workflow.workflow_id,
                        success=False,
                        step_results=step_results,
                        error=str(e),
                        execution_time_ms=(time.time() - start_time) * 1000
                    )

                state.current_step_index += 1
                state.variables = context.variables
                self.checkpoint.save_checkpoint(state)

            state.status = ExecutionStatus.COMPLETED
            self.checkpoint.clear_checkpoint(workflow.workflow_id)
            await self.events.publish_completed(workflow.workflow_id, success=True)
            return WorkflowResult(
                workflow_id=workflow.workflow_id,
                success=True,
                step_results=step_results,
                execution_time_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            await self.events.publish_completed(workflow.workflow_id, success=False, error=str(e))
            return WorkflowResult(
                workflow_id=workflow.workflow_id,
                success=False,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000
            )
