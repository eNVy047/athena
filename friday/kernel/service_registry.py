from typing import Dict, Any, Optional

class ServiceRegistry:
    """Registry managing active OS service life cycles."""
    def __init__(self):
        self._services: Dict[str, Any] = {}

    def register_service(self, name: str, service: Any) -> None:
        self._services[name] = service

    def get_service(self, name: str) -> Optional[Any]:
        return self._services.get(name)

    def remove_service(self, name: str) -> None:
        self._services.pop(name, None)

    def clear(self) -> None:
        self._services.clear()
