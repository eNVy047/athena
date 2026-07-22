import asyncio
import logging
import time
from typing import Dict, Any, Callable, Coroutine
from friday.core.cognition.models import Plan, TaskStatus, ExecutionResult
from friday.events.event_bus import EventBus
from friday.runtime.worker_manager import WorkerManager
from friday.runtime.checkpoint import CheckpointSystem
from friday.runtime.progress_tracker import ProgressTracker
from friday.runtime.runtime_events import JOB_STARTED, JOB_COMPLETED, JOB_FAILED

logger = logging.getLogger(__name__)

class JobExecutor:
    """Coordinates plan task lists across the worker pool and updates checkpoint states."""
    def __init__(
        self,
        event_bus: EventBus,
        worker_manager: WorkerManager,
        checkpoint_system: CheckpointSystem,
        progress_tracker: ProgressTracker,
        action_handlers: Dict[str, Callable[[Dict[str, Any]], Coroutine[Any, Any, Any]]]
    ):
        self.event_bus = event_bus
        self.worker_manager = worker_manager
        self.checkpoint_system = checkpoint_system
        self.progress_tracker = progress_tracker
        self.action_handlers = action_handlers

    async def execute_job(self, plan: Plan) -> bool:
        job_id = plan.id
        logger.info(f"Starting execution for Job Plan: {job_id}")
        await self.event_bus.publish(JOB_STARTED, {"job_id": job_id})
        
        total_tasks = len(plan.tasks)
        self.progress_tracker.start_job(job_id, total_steps=total_tasks)
        
        completed_tasks = 0
        
        # Execute tasks topologically
        while completed_tasks < total_tasks:
            runnable = [
                t for t in plan.tasks.values()
                if t.status == TaskStatus.PENDING and all(
                    dep in plan.tasks and plan.tasks[dep].status == TaskStatus.COMPLETED for dep in t.dependencies
                )
            ]
            
            if not runnable:
                # Cyclic dependencies or deadlocks
                break

            for task in runnable:
                worker = self.worker_manager.get_idle_worker()
                if not worker:
                    # Instantiate dynamic worker if none idle
                    worker = await self.worker_manager.create_worker(
                        f"worker_{completed_tasks}", self.action_handlers
                    )

                # Save checkpoint state
                self.checkpoint_system.create_checkpoint(
                    job_id=job_id, current_task=task.id, progress=(completed_tasks / total_tasks) * 100, context_data={}
                )

                success = await worker.execute_task(task)
                if not success:
                    task.status = TaskStatus.FAILED
                    await self.event_bus.publish(JOB_FAILED, {"job_id": job_id, "failed_task": task.id})
                    self.progress_tracker.complete_job(job_id, status="failed")
                    return False
                
                completed_tasks += 1
                self.progress_tracker.update_step(job_id, current_step=completed_tasks)

        self.checkpoint_system.clear_checkpoint(job_id)
        self.progress_tracker.complete_job(job_id, status="completed")
        await self.event_bus.publish(JOB_COMPLETED, {"job_id": job_id})
        return True
