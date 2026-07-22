import time
from typing import Dict, Any, List

class ProgressTracker:
    """Tracks step metrics, completion state, and execution ETAs."""
    def __init__(self):
        self._progress: Dict[str, Dict[str, Any]] = {}

    def start_job(self, job_id: str, total_steps: int) -> None:
        self._progress[job_id] = {
            "status": "running",
            "progress": 0.0,
            "current_step": 0,
            "total_steps": total_steps,
            "remaining_steps": total_steps,
            "eta": 0.0,
            "start_time": time.time(),
            "errors": [],
            "retries": 0
        }

    def update_step(self, job_id: str, current_step: int, errors: List[str] = None, retries: int = 0) -> None:
        if job_id not in self._progress:
            return
        job = self._progress[job_id]
        job["current_step"] = current_step
        job["remaining_steps"] = max(0, job["total_steps"] - current_step)
        job["progress"] = (current_step / job["total_steps"]) * 100.0 if job["total_steps"] > 0 else 100.0
        
        elapsed = time.time() - job["start_time"]
        if current_step > 0:
            avg_time = elapsed / current_step
            job["eta"] = avg_time * job["remaining_steps"]
        
        if errors:
            job["errors"].extend(errors)
        job["retries"] += retries

    def complete_job(self, job_id: str, status: str = "completed") -> None:
        if job_id in self._progress:
            self._progress[job_id]["status"] = status
            self._progress[job_id]["progress"] = 100.0
            self._progress[job_id]["remaining_steps"] = 0

    def get_progress(self, job_id: str) -> Dict[str, Any]:
        return self._progress.get(job_id, {})
