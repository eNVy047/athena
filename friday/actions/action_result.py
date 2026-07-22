from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ActionResult(BaseModel):
    success: bool
    output: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    logs: List[str] = Field(default_factory=list)
    telemetry: Dict[str, Any] = Field(default_factory=dict)
