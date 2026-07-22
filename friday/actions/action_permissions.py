from __future__ import annotations

import logging
from typing import Optional, Any
from friday.actions.action_models import ActionRequest, ActionType

logger = logging.getLogger("friday-agent")

class PermissionManager:
    def __init__(self, security_manager: Optional[Any] = None):
        self.security_manager = security_manager
        # Sensitive action list
        self.sensitive_actions = {
            ActionType.TERMINAL: ["run_command"],
            ActionType.FILESYSTEM: ["delete", "write", "rename"],
            ActionType.POWER: ["shutdown", "reboot"],
            ActionType.BROWSER: ["execute_javascript"]
        }

    def is_sensitive(self, request: ActionRequest) -> bool:
        category_sensitive = self.sensitive_actions.get(request.action_type, [])
        return request.command in category_sensitive or request.action_type in [ActionType.POWER, ActionType.TERMINAL]

    async def check_permission(self, request: ActionRequest) -> bool:
        """Verifies if the action has appropriate execution privileges."""
        if not self.is_sensitive(request):
            return True

        action_name = f"{request.action_type.value}.{request.command}"
        if self.security_manager:
            try:
                # Delegate to core SecurityManager
                return await self.security_manager.authorize_action(action_name, sensitive=True)
            except Exception as e:
                logger.error(f"[PermissionManager] Authorization error: {e}")
                return False
                
        # Default fallback: decline sensitive actions if no SecurityManager is registered
        logger.warning(f"[PermissionManager] Declining unauthorized action: {action_name}")
        return False
