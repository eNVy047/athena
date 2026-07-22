from __future__ import annotations

import time
from typing import Any, Dict

class WorkflowContext:
    def __init__(self, workflow_id: str, initial_variables: Dict[str, Any] = None):
        self.workflow_id = workflow_id
        self.variables = initial_variables or {}
        self.start_time = time.time()

    def get_variable(self, key: str, default: Any = None) -> Any:
        return self.variables.get(key, default)

    def set_variable(self, key: str, value: Any) -> None:
        self.variables[key] = value

    def get_duration_ms(self) -> float:
        return (time.time() - self.start_time) * 1000
