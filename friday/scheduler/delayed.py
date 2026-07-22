from datetime import datetime
from pydantic import BaseModel

class DelayedTask(BaseModel):
    task_id: str
    run_at: datetime
    
    def is_due(self, now: datetime) -> bool:
        return now >= self.run_at
