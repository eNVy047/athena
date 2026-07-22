import json
import os
from typing import Dict, Any
from friday.runtime.state_store import StateStore

class CheckpointSystem:
    """Manages active job checkpoints to allow resume operations after restart/crashes."""
    def __init__(self, state_store: StateStore):
        self.state_store = state_store

    def create_checkpoint(self, job_id: str, current_task: str, progress: float, context_data: Dict[str, Any]) -> None:
        checkpoint_data = {
            "job_id": job_id,
            "current_task": current_task,
            "progress": progress,
            "context": context_data,
            "timestamp": str(os.times())
        }
        active_jobs = self.state_store.get("active_jobs", {})
        active_jobs[job_id] = checkpoint_data
        self.state_store.update("active_jobs", active_jobs)
        self.state_store.save()

    def get_checkpoint(self, job_id: str) -> Dict[str, Any]:
        return self.state_store.get("active_jobs", {}).get(job_id, {})

    def clear_checkpoint(self, job_id: str) -> None:
        active_jobs = self.state_store.get("active_jobs", {})
        if job_id in active_jobs:
            del active_jobs[job_id]
            self.state_store.update("active_jobs", active_jobs)
            self.state_store.save()
