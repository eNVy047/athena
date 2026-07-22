import json
import os
from typing import Dict, Any

class StateStore:
    """Thread-safe persistent state store for runtime, scheduler, and workers."""
    def __init__(self, persistence_path: str = "./runtime_state_store.json"):
        self.persistence_path = persistence_path
        self._state: Dict[str, Any] = {
            "runtime_status": "idle",
            "workers": {},
            "active_jobs": {},
            "scheduler_jobs": []
        }

    def update(self, category: str, data: Any) -> None:
        self._state[category] = data

    def get(self, category: str, default: Any = None) -> Any:
        return self._state.get(category, default)

    def save(self) -> None:
        with open(self.persistence_path, "w") as f:
            json.dump(self._state, f)

    def load(self) -> None:
        if os.path.exists(self.persistence_path):
            with open(self.persistence_path, "r") as f:
                self._state = json.load(f)
