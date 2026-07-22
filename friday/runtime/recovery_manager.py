import logging
from typing import Any, Callable, Coroutine
from friday.runtime.checkpoint import CheckpointSystem

logger = logging.getLogger(__name__)

class RecoveryManager:
    """Restores plan checkpoints and recovers interrupted jobs after startup."""
    def __init__(self, checkpoint_system: CheckpointSystem):
        self.checkpoint_system = checkpoint_system

    async def recover_active_jobs(self, resume_handler: Callable[[str, Any], Coroutine[Any, Any, None]]) -> None:
        active_jobs = self.checkpoint_system.state_store.get("active_jobs", {})
        if not active_jobs:
            logger.info("No active checkpoints found for recovery.")
            return

        logger.info(f"Found {len(active_jobs)} checkpoints. Starting recovery...")
        for job_id, data in list(active_jobs.items()):
            logger.info(f"Recovering Job: {job_id} starting at task {data['current_task']}")
            try:
                await resume_handler(job_id, data)
            except Exception as e:
                logger.error(f"Failed to recover Job {job_id}: {e}")
