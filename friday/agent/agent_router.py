from __future__ import annotations

from typing import Dict, Any

class AgentRouter:
    def route_request(self, query: str) -> Dict[str, Any]:
        """Routes conversational requests to appropriate automation pipelines or skills."""
        query_lower = query.lower()
        if "workflow" in query_lower or "automate" in query_lower:
            return {"route": "automation", "action": "run_workflow"}
        elif "click" in query_lower or "type" in query_lower or "move" in query_lower:
            return {"route": "action_layer", "action": "low_level_action"}
        return {"route": "cognition", "action": "reason"}
