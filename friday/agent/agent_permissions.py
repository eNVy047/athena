from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger("friday-agent")

class AgentPermissionManager:
    def __init__(self, security_manager: Optional[Any] = None):
        self.security_manager = security_manager

    async def check_request_permissions(self, user_id: str, request_type: str) -> bool:
        """Verifies if the requested task type is authorized for the given User ID."""
        if not self.security_manager:
            return True
        try:
            return await self.security_manager.authorize_action(f"agent.request.{request_type}", sensitive=False)
        except Exception as e:
            logger.error(f"[AgentPermissions] Failed to complete permission check: {e}")
            return False
