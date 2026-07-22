from __future__ import annotations

import logging
from typing import Any, Optional
from friday.automation.workflow_models import Workflow

logger = logging.getLogger("friday-agent")

class WorkflowPermissionManager:
    def __init__(self, security_manager: Optional[Any] = None):
        self.security_manager = security_manager

    async def check_workflow_permissions(self, workflow: Workflow) -> bool:
        """Verifies if the workflow as a whole is authorized for execution."""
        if not self.security_manager:
            return True
        try:
            # Sensitive operations inside steps might trigger warnings
            return await self.security_manager.authorize_action(f"workflow.{workflow.workflow_id}", sensitive=False)
        except Exception as e:
            logger.error(f"[WorkflowPermissions] Failed permission check: {e}")
            return False
