import asyncio
import logging
from friday.events.event_bus import EventBus
from friday.events.event_types import Event

logger = logging.getLogger(__name__)

class EventDispatcher:
    """Manages event dispatching queues and asynchronous routing loops."""
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._queue: asyncio.Queue[Event] = asyncio.Queue()
        self._loop_task: asyncio.Task | None = None

    def enqueue(self, event: Event) -> None:
        self._queue.put_nowait(event)

    def start(self) -> None:
        self._loop_task = asyncio.create_task(self._routing_loop())
        logger.info("Event Dispatcher routing loop started.")

    async def stop(self) -> None:
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass
        logger.info("Event Dispatcher routing loop stopped.")

    async def _routing_loop(self) -> None:
        while True:
            event = await self._queue.get()
            try:
                await self.event_bus.publish(event.event_type, event)
            except Exception as e:
                logger.error(f"Failed routing event {event.event_type}: {e}")
            finally:
                self._queue.task_done()
