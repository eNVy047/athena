from __future__ import annotations

from typing import Optional
from pydantic import BaseModel

class AgentSession(BaseModel):
    conversation_id: str
    user_id: str
    task_id: Optional[str] = None
    execution_id: Optional[str] = None
    request_id: Optional[str] = None
    workflow_id: Optional[str] = None
