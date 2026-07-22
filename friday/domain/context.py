from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ExecutionContext(BaseModel):
    session_id: str
    user_id: str
    chat_history: List[ChatMessage] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    active_skills: List[str] = Field(default_factory=list)
