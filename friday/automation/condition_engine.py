from __future__ import annotations

import asyncio
from typing import Any, Dict

class ConditionEngine:
    def evaluate(self, expression: str, variables: Dict[str, Any]) -> bool:
        """Evaluates condition expressions in python-like format."""
        if not expression:
            return True
        try:
            # Safe evaluation with restricted globals/locals
            return bool(eval(expression, {"__builtins__": None}, variables))
        except Exception:
            return False

    async def wait_until(self, check_callback: Any, interval: float = 0.5, timeout: float = 10.0) -> bool:
        """Blocks execution until the check callback evaluates to true or timeout occurs."""
        start = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start) < timeout:
            if asyncio.iscoroutinefunction(check_callback):
                res = await check_callback()
            else:
                res = check_callback()
            if res:
                return True
            await asyncio.sleep(interval)
        return False
