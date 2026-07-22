from typing import Dict, Any, Optional
from friday.core.cognition.models import Plan

class JobStore:
    """In-memory and persistent storage for Job plans and execution histories."""
    def __init__(self):
        self._jobs: Dict[str, Plan] = {}

    def store_job(self, job_id: str, plan: Plan) -> None:
        self._jobs[job_id] = plan

    def get_job(self, job_id: str) -> Optional[Plan]:
        return self._jobs.get(job_id)

    def remove_job(self, job_id: str) -> None:
        if job_id in self._jobs:
            del self._jobs[job_id]
