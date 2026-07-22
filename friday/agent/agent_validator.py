from __future__ import annotations

from typing import Any, Dict

class AgentValidator:
    def validate_request(self, payload: Dict[str, Any]) -> bool:
        """Inspects request payload arguments before running Agent pipeline."""
        if not payload:
            raise ValueError("Request payload cannot be empty.")
        if "user_id" not in payload:
            raise ValueError("user_id parameter is required in request payload.")
        if "query" not in payload:
            raise ValueError("query parameter is required in request payload.")
        return True
