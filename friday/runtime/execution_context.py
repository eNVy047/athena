from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class ExecutionContext:
    """Active execution environment context containing bindings and metadata."""
    job_id: str
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def set(self, key: str, value: Any) -> None:
        self.variables[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.variables.get(key, default)
