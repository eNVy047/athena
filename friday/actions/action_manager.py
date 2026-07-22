from __future__ import annotations

import logging
from typing import Any, Optional
from friday.actions.action_models import ActionRequest
from friday.actions.action_result import ActionResult
from friday.actions.action_context import ActionContext
from friday.actions.action_permissions import PermissionManager
from friday.actions.action_validator import ActionValidator
from friday.actions.action_history import ActionHistory
from friday.actions.action_events import ActionEvents
from friday.actions.action_executor import ActionExecutor
from friday.actions.action_scheduler import ActionScheduler

logger = logging.getLogger("friday-agent")

class ActionManager:
    def __init__(self, security_manager: Optional[Any] = None, event_bus: Optional[Any] = None):
        self.permissions = PermissionManager(security_manager)
        self.validator = ActionValidator()
        self.history = ActionHistory()
        self.events = ActionEvents(event_bus)
        self.executor = ActionExecutor()
        self.scheduler = ActionScheduler()

    def initialize(self) -> None:
        # Start background task queue
        self.scheduler.start(self.execute_scheduled)
        logger.info("[ActionManager] Action Layer initialized successfully.")

    async def shutdown(self) -> None:
        await self.scheduler.stop()
        logger.info("[ActionManager] Action Layer shut down.")

    async def execute_action(self, request: ActionRequest) -> ActionResult:
        """Central execution routine: validates parameters, checks permissions, publishes events, and runs action."""
        context = ActionContext()
        await self.events.publish_started(request)
        
        # 1. Validation check
        try:
            self.validator.validate(request)
        except Exception as e:
            result = ActionResult(success=False, error=f"Validation failed: {e}")
            await self.events.publish_completed(request, result)
            return result
            
        # 2. Permission check
        allowed = await self.permissions.check_permission(request)
        if not allowed:
            result = ActionResult(success=False, error="Action denied by security permissions.")
            await self.events.publish_completed(request, result)
            return result

        # 3. Execution
        result = await self.executor.execute(request, context)
        
        # 4. History log
        self.history.record(request, result)
        
        # 5. Dispatch completion event
        await self.events.publish_completed(request, result)
        
        return result

    async def execute_scheduled(self, request: ActionRequest) -> None:
        """Callback invoked by background queue to execute scheduled requests."""
        await self.execute_action(request)
