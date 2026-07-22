from typing import List, Dict, Set

class DependencyGraph:
    """Manages system bootstrap order and dependency resolution."""
    def __init__(self):
        self._dependencies: Dict[str, Set[str]] = {}

    def add_service(self, name: str, depends_on: List[str]) -> None:
        self._dependencies[name] = set(depends_on)

    def resolve_bootstrap_order(self) -> List[str]:
        visited: Set[str] = set()
        temp: Set[str] = set()
        order: List[str] = []

        def visit(node: str):
            if node in temp:
                raise ValueError(f"Circular dependency detected at service: {node}")
            if node not in visited:
                temp.add(node)
                for neighbor in self._dependencies.get(node, []):
                    visit(neighbor)
                temp.remove(node)
                visited.add(node)
                order.append(node)

        for service in self._dependencies:
            if service not in visited:
                visit(service)
        return order
