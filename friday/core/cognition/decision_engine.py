import uuid
from typing import Dict, Any, List, Optional
from friday.core.cognition.models import Decision

class DecisionEngine:
    """Evaluates multiple actions and chooses the optimal strategy."""
    def __init__(self):
        self._rules: List[Dict[str, Any]] = []

    def add_rule(self, trigger_condition: str, action: str, confidence: float = 1.0) -> None:
        self._rules.append({
            "condition": trigger_condition,
            "action": action,
            "confidence": confidence
        })

    async def decide(self, context: Dict[str, Any], candidates: List[str]) -> Decision:
        # Check rule-based decisions first
        for rule in self._rules:
            if rule["condition"] in context.get("state", ""):
                return Decision(
                    id=str(uuid.uuid4()),
                    chosen_action=rule["action"],
                    confidence=rule["confidence"],
                    rationale=f"Rule matched: {rule['condition']}"
                )

        # Fallback to the first candidate or unknown default action
        chosen = candidates[0] if candidates else "default.unknown"
        return Decision(
            id=str(uuid.uuid4()),
            chosen_action=chosen,
            confidence=0.5,
            rationale="No matching rules; chose default or fallback action."
        )
