from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class WorkflowStep(BaseModel):
    step_id: str
    name: str
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Any] = None
    error: Optional[str] = None

class WorkflowState(BaseModel):
    workflow_id: str
    name: str
    steps: List[WorkflowStep] = Field(default_factory=list)
    context_data: Dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"  # pending, running, completed, failed, paused
    current_step_id: Optional[str] = None
