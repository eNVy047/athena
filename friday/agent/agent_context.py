from __future__ import annotations

from typing import Any, Dict, List
from pydantic import BaseModel, Field

class AgentContext(BaseModel):
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    working_memory: List[Dict[str, Any]] = Field(default_factory=list)
    perception_snapshot: Dict[str, Any] = Field(default_factory=dict)
    world_state: Dict[str, Any] = Field(default_factory=dict)
    running_workflows: List[str] = Field(default_factory=list)
    current_applications: List[str] = Field(default_factory=list)
    open_windows: List[str] = Field(default_factory=list)
    clipboard: str = ""
