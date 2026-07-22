import logging
from typing import Callable, Coroutine, Any

logger = logging.getLogger(__name__)

class SecurityManager:
    """Enforces execution permission rules and user confirmation checks."""
    def __init__(self):
        self._approval_callback: Callable[[str], Coroutine[Any, Any, bool]] = self._default_approval

    def set_approval_handler(self, handler: Callable[[str], Coroutine[Any, Any, bool]]) -> None:
        self._approval_callback = handler

    async def _default_approval(self, action: str) -> bool:
        logger.warning(f"No explicit approval handler registered. Declining sensitive action: {action}")
        return False

    async def authorize_action(self, action_name: str, sensitive: bool = False) -> bool:
        if not sensitive:
            return True
        logger.info(f"Sensitive action requested: {action_name}. Requesting user approval...")
        return await self._approval_callback(action_name)
