from typing import Protocol, Any, Dict

class LearningEngine(Protocol):
    """Abstract interface for future reinforcement/supervised behavior updates."""
    async def update_policy(self, state: Dict[str, Any], action: str, reward: float) -> None:
        ...

class PlaceholderLearningEngine:
    """Non-ML placeholder implementation of the Learning Engine interface."""
    def __init__(self):
        self.history = []

    async def update_policy(self, state: Dict[str, Any], action: str, reward: float) -> None:
        self.history.append((state, action, reward))
