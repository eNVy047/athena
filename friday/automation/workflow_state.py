from __future__ import annotations

from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel, Field

class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowState(BaseModel):
    workflow_id: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    current_step_index: int = 0
    variables: Dict[str, Any] = Field(default_factory=dict)
    errors: Dict[str, str] = Field(default_factory=dict)
