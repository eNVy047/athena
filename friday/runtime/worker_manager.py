from typing import Dict, List, Callable, Coroutine, Any, Optional
from friday.runtime.worker import Worker
from friday.events.event_bus import EventBus
from friday.runtime.runtime_events import WORKER_CREATED, WORKER_STOPPED

class WorkerManager:
    """Manages worker pool instantiation, assignment, and status checks."""
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._workers: Dict[str, Worker] = {}

    async def create_worker(self, worker_id: str, handlers: Dict[str, Callable[[Dict[str, Any]], Coroutine[Any, Any, Any]]]) -> Worker:
        worker = Worker(worker_id, handlers)
        self._workers[worker_id] = worker
        await self.event_bus.publish(WORKER_CREATED, {"worker_id": worker_id})
        return worker

    async def stop_worker(self, worker_id: str) -> None:
        if worker_id in self._workers:
            del self._workers[worker_id]
            await self.event_bus.publish(WORKER_STOPPED, {"worker_id": worker_id})

    def get_idle_worker(self) -> Optional[Worker]:
        for w in self._workers.values():
            if w.is_idle:
                return w
        return None

    def worker_count(self) -> int:
        return len(self._workers)
