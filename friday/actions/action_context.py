from __future__ import annotations

import time
from typing import Any, Dict

class ActionContext:
    def __init__(self, metadata: Dict[str, Any] = None):
        self.metadata = metadata or {}
        self.start_time = time.time()
        self.workspace_root = "/Users/narayanverma/Documents/jarvis/friday"

    def get_duration_ms(self) -> float:
        return (time.time() - self.start_time) * 1000
