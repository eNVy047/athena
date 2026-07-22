from datetime import datetime, timedelta
from pydantic import BaseModel, Field

class RecurringTask(BaseModel):
    task_id: str
    interval_seconds: float
    last_run: datetime = Field(default_factory=datetime.utcnow)
    
    def is_due(self, now: datetime) -> bool:
        return (now - self.last_run).total_seconds() >= self.interval_seconds
