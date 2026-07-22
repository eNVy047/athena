from typing import Dict, Any, Type, TypeVar

T = TypeVar("T")

class Container:
    def __init__(self):
        self._registry: Dict[Type, Any] = {}

    def register(self, interface: Type[T], implementation: Any):
        self._registry[interface] = implementation

    def resolve(self, interface: Type[T]) -> T:
        if interface not in self._registry:
            raise KeyError(f"Interface {interface.__name__} has not been registered in the DI Container.")
        return self._registry[interface]

container = Container()
