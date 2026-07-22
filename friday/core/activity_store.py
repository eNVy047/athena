from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class ActivityRecord(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    conversation_id: str
    user_request: str
    selected_tools: List[str] = Field(default_factory=list)
    execution_duration: float
    error_message: Optional[str] = None

class ActivityStore:
    def __init__(self):
        self._records: List[ActivityRecord] = []

    def record(self, record: ActivityRecord):
        self._records.append(record)

    def get_records(self) -> List[ActivityRecord]:
        return self._records
