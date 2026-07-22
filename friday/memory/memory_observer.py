import logging
from typing import Optional
from friday.events.event_bus import EventBus
from friday.events.event_types import Event
from friday.memory.memory_models import MemoryEntry, MemoryType

logger = logging.getLogger("friday-agent")


class MemoryObserver:
    def __init__(self, event_bus: Optional[EventBus] = None):
        self.event_bus = event_bus
        self.memory_manager = None

    def set_memory_manager(self, memory_manager) -> None:
        self.memory_manager = memory_manager

    def initialize(self) -> None:
        if self.event_bus:
            # Subscribe to perception or action completion events
            self.event_bus.subscribe("perception.observation", self.on_observation)
            self.event_bus.subscribe("action.completed", self.on_action_completed)
            logger.info("[MemoryObserver] Subscribed to perception & action events.")

    async def on_observation(self, event: Event) -> None:
        """Handles new perception observations and converts them to memories."""
        if not self.memory_manager:
            return

        data = event.data
        sensor_name = data.get("sensor_name", "unknown")
        normalized = data.get("normalized_data", "")

        if normalized:
            content = f"Observed from {sensor_name}: {normalized}"
            entry = MemoryEntry(
                content=content,
                memory_type=MemoryType.EPISODIC,
                metadata={"sensor_name": sensor_name, "source": "perception"},
            )
            await self.memory_manager.store_memory(entry)
            logger.debug("[MemoryObserver] Stored episodic memory from observation.")

    async def on_action_completed(self, event: Event) -> None:
        """Handles actions completed by the agent and registers them in procedural/episodic memory."""
        if not self.memory_manager:
            return

        data = event.data
        action_name = data.get("action_name") or data.get("tool_name", "unknown")
        success = data.get("success", True)
        result = data.get("result", "")

        content = f"Executed tool/action '{action_name}' with success={success}. Result: {result}"
        entry = MemoryEntry(
            content=content,
            memory_type=MemoryType.PROCEDURAL if success else MemoryType.EPISODIC,
            metadata={
                "action_name": action_name,
                "success": success,
                "source": "action",
            },
        )
        await self.memory_manager.store_memory(entry)
        logger.debug(f"[MemoryObserver] Stored action memory: {action_name}")
