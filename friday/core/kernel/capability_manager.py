from typing import Dict, Set

class CapabilityManager:
    """Manages active system feature sets and capabilities."""
    def __init__(self):
        self._capabilities: Dict[str, bool] = {}

    def register_capability(self, name: str, enabled: bool = True) -> None:
        self._capabilities[name] = enabled

    def enable(self, name: str) -> None:
        self._capabilities[name] = True

    def disable(self, name: str) -> None:
        self._capabilities[name] = False

    def is_enabled(self, name: str) -> bool:
        return self._capabilities.get(name, False)
