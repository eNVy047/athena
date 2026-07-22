from __future__ import annotations

from typing import Any, List, Optional
from pydantic import BaseModel, Field

class StepResult(BaseModel):
    step_id: str
    success: bool
    output: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0

class WorkflowResult(BaseModel):
    workflow_id: str
    success: bool
    step_results: List[StepResult] = Field(default_factory=list)
    error: Optional[str] = None
    execution_time_ms: float = 0.0
