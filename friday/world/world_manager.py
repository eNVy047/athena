import logging
from typing import Optional, Dict, Any
from friday.core.kernel.kernel import FridayKernel
from friday.events.event_bus import EventBus
from friday.world.entity_store import InMemoryEntityStoreProvider, EntityStoreProvider
from friday.world.relationship_graph import InMemoryRelationshipStoreProvider, RelationshipStoreProvider
from friday.world.knowledge_graph import KnowledgeGraph
from friday.world.timeline import Timeline
from friday.world.state_tracker import StateTracker
from friday.world.environment import EnvironmentManager
from friday.world.device_manager import DeviceManager
from friday.world.people_manager import PeopleManager
from friday.world.project_manager import ProjectManager
from friday.world.location_manager import LocationManager
from friday.world.inventory import InventoryManager
from friday.world.world_events import WorldEvent, WorldEventPayload

logger = logging.getLogger(__name__)

class WorldManager:
    def __init__(
        self,
        kernel: FridayKernel,
        event_bus: EventBus,
        entity_store: Optional[EntityStoreProvider] = None,
        relationship_graph: Optional[RelationshipStoreProvider] = None
    ):
        self.kernel = kernel
        self.event_bus = event_bus

        # Allow pluggable providers
        self.entity_store = entity_store or InMemoryEntityStoreProvider()
        self.relationship_graph = relationship_graph or InMemoryRelationshipStoreProvider()

        # Core Graph and Timeline
        self.knowledge_graph = KnowledgeGraph(self.entity_store, self.relationship_graph)
        self.timeline = Timeline()

        # Managers
        self.state_tracker = StateTracker()
        self.environment = EnvironmentManager()
        self.device_manager = DeviceManager(self.knowledge_graph)
        self.people_manager = PeopleManager(self.knowledge_graph)
        self.project_manager = ProjectManager(self.knowledge_graph)
        self.location_manager = LocationManager(self.knowledge_graph)
        self.inventory_manager = InventoryManager(self.knowledge_graph)

        # Register inside the Kernel & DI container
        if hasattr(self.kernel, "services"):
            self.kernel.services.register(WorldManager, self)
        if hasattr(self.kernel, "registry"):
            if hasattr(self.kernel.registry, "register"):
                self.kernel.registry.register(WorldManager, self)
            elif hasattr(self.kernel.registry, "register_service"):
                self.kernel.registry.register_service("WorldManager", self)

        try:
            from friday.core.di import container
            container.register(WorldManager, self)
        except Exception:
            pass

    async def publish_world_event(self, event_type: str, data: Dict[str, Any]) -> None:
        payload = WorldEventPayload(event_type, data)
        await self.event_bus.publish(event_type, payload.to_dict())

    # Wrapper helper methods that publish events automatically
    async def add_device(self, device_id: str, name: str, device_class: str, properties: Optional[Dict[str, Any]] = None) -> None:
        device = self.device_manager.add_device(device_id, name, device_class, properties)
        self.timeline.record_event(device_id, "creation", {"name": name, "class": device_class})
        self.state_tracker.add_device(device_id)
        await self.publish_world_event(WorldEvent.DEVICE_ADDED, device.to_dict())

    async def remove_device(self, device_id: str) -> None:
        device = self.device_manager.get_device(device_id)
        if device:
            device_dict = device.to_dict()
            self.device_manager.remove_device(device_id)
            self.timeline.record_event(device_id, "deletion")
            self.state_tracker.remove_device(device_id)
            await self.publish_world_event(WorldEvent.DEVICE_REMOVED, device_dict)

    async def create_project(self, project_id: str, name: str, properties: Optional[Dict[str, Any]] = None) -> None:
        project = self.project_manager.add_project(project_id, name, properties)
        self.timeline.record_event(project_id, "creation", {"name": name})
        await self.publish_world_event(WorldEvent.PROJECT_CREATED, project.to_dict())

    def update_state(self, category: str, updates: Dict[str, Any]):
        """Updates internal state and tracks changes."""
        # Simple passthrough to state tracker or environment
        logger.info(f"World state updated for {category}: {updates}")
        if not hasattr(self.state_tracker, 'state'):
            self.state_tracker.state = {}
        if category not in self.state_tracker.state:
            self.state_tracker.state[category] = {}
        self.state_tracker.state[category].update(updates)

    async def change_location(self, location_id: str, name: str, properties: Optional[Dict[str, Any]] = None) -> None:
        loc = self.location_manager.add_location(location_id, name, properties)
        self.state_tracker.set_location(location_id)
        self.timeline.record_event(location_id, "accessed", {"name": name})
        await self.publish_world_event(WorldEvent.LOCATION_CHANGED, loc.to_dict())
