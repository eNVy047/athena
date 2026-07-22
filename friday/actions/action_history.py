from __future__ import annotations

import logging
from typing import List, Tuple, Any, Optional
from friday.actions.action_models import ActionRequest
from friday.actions.action_result import ActionResult

logger = logging.getLogger("friday-agent")

class ActionHistory:
    def __init__(self):
        # Stores history as a list of tuples: (ActionRequest, ActionResult, undo_data)
        self.history: List[Tuple[ActionRequest, ActionResult, Any]] = []

    def record(self, request: ActionRequest, result: ActionResult, undo_data: Any = None) -> None:
        self.history.append((request, result, undo_data))
        logger.debug(f"[ActionHistory] Recorded action: {request.action_type.value}.{request.command}")

    def get_last_action(self) -> Optional[Tuple[ActionRequest, ActionResult, Any]]:
        if not self.history:
            return None
        return self.history[-1]

    def clear(self) -> None:
        self.history.clear()
