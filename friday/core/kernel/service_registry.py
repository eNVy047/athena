from typing import Dict, Type, Any

class ServiceRegistry:
    """Registry locator for core subsystems within the Friday OS Kernel."""
    def __init__(self):
        self._services: Dict[Type[Any], Any] = {}

    def register(self, interface: Type[Any], instance: Any) -> None:
        self._services[interface] = instance

    def get(self, interface: Type[Any]) -> Any:
        if interface not in self._services:
            raise KeyError(f"Service {interface.__name__} not registered in Kernel.")
        return self._services[interface]

    def has(self, interface: Type[Any]) -> bool:
        return interface in self._services
