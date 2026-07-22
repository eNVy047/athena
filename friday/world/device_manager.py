from typing import List, Dict, Any, Optional
from friday.world.knowledge_graph import KnowledgeGraph
from friday.world.entity import WorldEntity
from friday.world.ontology import EntityType

class DeviceManager:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.graph = knowledge_graph

    def add_device(self, device_id: str, name: str, device_type: str, properties: Optional[Dict[str, Any]] = None) -> WorldEntity:
        props = properties or {}
        props.update({"name": name, "device_class": device_type})
        entity = WorldEntity(device_id, EntityType.DEVICE, props)
        self.graph.add_entity(entity)
        return entity

    def get_device(self, device_id: str) -> Optional[WorldEntity]:
        entity = self.graph.get_entity(device_id)
        if entity and entity.type == EntityType.DEVICE:
            return entity
        return None

    def list_devices(self) -> List[WorldEntity]:
        return self.graph.list_entities(EntityType.DEVICE)

    def remove_device(self, device_id: str) -> None:
        device = self.get_device(device_id)
        if device:
            self.graph.delete_entity(device_id)
