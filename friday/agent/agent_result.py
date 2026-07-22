from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel

class AgentResult(BaseModel):
    success: bool
    output: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
