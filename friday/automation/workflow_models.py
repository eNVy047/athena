from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class WorkflowStep(BaseModel):
    step_id: str
    action_type: str
    command: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    parallel: bool = False
    condition: Optional[str] = None # e.g. "if x == 1" or "wait_until_file_exists"
    rollback_command: Optional[str] = None
    rollback_arguments: Dict[str, Any] = Field(default_factory=dict)

class Trigger(BaseModel):
    trigger_type: str # "time", "file_change", "clipboard_change", "custom_event"
    config: Dict[str, Any] = Field(default_factory=dict)

class Workflow(BaseModel):
    workflow_id: str
    name: str
    description: str = ""
    steps: List[WorkflowStep] = Field(default_factory=list)
    triggers: List[Trigger] = Field(default_factory=list)
    max_retries: int = 0
    retry_delay_seconds: float = 1.0
    timeout_seconds: float = 60.0
