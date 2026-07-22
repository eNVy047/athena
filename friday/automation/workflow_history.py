from __future__ import annotations

import logging
from typing import List, Optional, Any
from friday.automation.workflow_result import WorkflowResult

logger = logging.getLogger("friday-agent")

class WorkflowHistory:
    def __init__(self, memory_manager: Optional[Any] = None):
        self.memory_manager = memory_manager
        self.history: List[WorkflowResult] = []

    async def record_run(self, result: WorkflowResult) -> None:
        self.history.append(result)
        status_str = "succeeded" if result.success else f"failed: {result.error}"
        log_msg = f"[WorkflowHistory] Workflow {result.workflow_id} completed. Status: {status_str}"
        logger.info(log_msg)

        # Integrate with Memory Layer
        if self.memory_manager:
            try:
                await self.memory_manager.store_memory(
                    content=f"Workflow run completed: ID={result.workflow_id}, success={result.success}, duration={result.execution_time_ms:.1f}ms. Logs: {log_msg}",
                    category="automation"
                )
            except Exception as e:
                logger.error(f"[WorkflowHistory] Failed to log run to Memory system: {e}")

    def get_runs(self, workflow_id: str) -> List[WorkflowResult]:
        return [r for r in self.history if r.workflow_id == workflow_id]
