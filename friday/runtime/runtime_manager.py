import asyncio
import logging
from typing import Dict, Any, Callable, Coroutine
from friday.core.kernel.kernel import FridayKernel
from friday.events.event_bus import EventBus
from friday.runtime.state_store import StateStore
from friday.runtime.checkpoint import CheckpointSystem
from friday.runtime.progress_tracker import ProgressTracker
from friday.runtime.retry_manager import RetryManager
from friday.runtime.timeout_manager import TimeoutManager
from friday.runtime.recovery_manager import RecoveryManager
from friday.runtime.job_store import JobStore
from friday.runtime.task_queue import TaskQueue
from friday.runtime.worker_manager import WorkerManager
from friday.runtime.job_executor import JobExecutor
from friday.runtime.scheduler import Scheduler
from friday.runtime.resource_monitor import ResourceMonitor
from friday.runtime.health_monitor import HealthMonitor

logger = logging.getLogger(__name__)

class RuntimeManager:
    """The unified manager orchestrating scheduler runs, job executions, and recovery pipelines."""
    def __init__(self, kernel: FridayKernel, event_bus: EventBus):
        self.kernel = kernel
        self.event_bus = event_bus

        # Initialize sub-components
        self.state_store = StateStore()
        self.checkpoint_system = CheckpointSystem(self.state_store)
        self.progress_tracker = ProgressTracker()
        self.retry_manager = RetryManager()
        self.timeout_manager = TimeoutManager()
        self.recovery_manager = RecoveryManager(self.checkpoint_system)
        self.job_store = JobStore()
        self.task_queue = TaskQueue()
        self.worker_manager = WorkerManager(self.event_bus)
        self.scheduler = Scheduler()
        self.resource_monitor = ResourceMonitor()
        self.health_monitor = HealthMonitor(self.resource_monitor, self.progress_tracker)

        # In-memory registration of handlers
        self._action_handlers: Dict[str, Callable[[Dict[str, Any]], Coroutine[Any, Any, Any]]] = {}

        self.job_executor = JobExecutor(
            self.event_bus,
            self.worker_manager,
            self.checkpoint_system,
            self.progress_tracker,
            self._action_handlers
        )

        # Register services inside DI container
        self.kernel.services.register(RuntimeManager, self)
        self.kernel.services.register(Scheduler, self.scheduler)
        self.kernel.services.register(HealthMonitor, self.health_monitor)

    def register_action_handler(
        self, action_name: str, handler: Callable[[Dict[str, Any]], Coroutine[Any, Any, Any]]
    ) -> None:
        self._action_handlers[action_name] = handler

    async def start(self) -> None:
        logger.info("Starting Friday Runtime Subsystem...")
        self.state_store.load()
        self.scheduler.start()
        
        # Trigger system recovery check
        await self.recovery_manager.recover_active_jobs(self._resume_job)
        logger.info("Friday Runtime Subsystem is ONLINE.")

    async def stop(self) -> None:
        logger.info("Stopping Friday Runtime Subsystem...")
        await self.scheduler.stop()
        self.state_store.save()
        logger.info("Friday Runtime Subsystem is OFFLINE.")

    async def _resume_job(self, job_id: str, checkpoint_data: Dict[str, Any]) -> None:
        # Load and restart execution flow for the given job_id
        plan = self.job_store.get_job(job_id)
        if plan:
            logger.info(f"Resuming task execution graph for Job ID: {job_id}")
            asyncio.create_task(self.job_executor.execute_job(plan))
