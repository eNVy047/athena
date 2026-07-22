import pytest
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ActivityRecord(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    conversation_id: str
    user_request: str
    selected_tools: List[str] = Field(default_factory=list)
    execution_duration: float
    error_message: Optional[str] = None

def test_activity_pipeline_schema():
    record = ActivityRecord(
        conversation_id="conv_85",
        user_request="Lock suit modules",
        selected_tools=["lock_suit"],
        execution_duration=0.150
    )
    
    assert record.conversation_id == "conv_85"
    assert "lock_suit" in record.selected_tools
    assert record.execution_duration == 0.150
