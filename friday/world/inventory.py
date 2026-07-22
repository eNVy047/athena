from typing import List, Dict, Any, Optional
from friday.world.knowledge_graph import KnowledgeGraph
from friday.world.entity import WorldEntity
from friday.world.ontology import EntityType

class InventoryManager:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.graph = knowledge_graph

    def track_process(self, process_id: str, name: str, properties: Optional[Dict[str, Any]] = None) -> WorldEntity:
        props = properties or {}
        props.update({"name": name, "pid": process_id})
        entity = WorldEntity(process_id, EntityType.PROCESS, props)
        self.graph.add_entity(entity)
        return entity

    def untrack_process(self, process_id: str) -> None:
        self.graph.delete_entity(process_id)

    def track_usb_device(self, usb_id: str, name: str, properties: Optional[Dict[str, Any]] = None) -> WorldEntity:
        props = properties or {}
        props.update({"name": name})
        entity = WorldEntity(usb_id, EntityType.USB_DEVICE, props)
        self.graph.add_entity(entity)
        return entity

    def untrack_usb_device(self, usb_id: str) -> None:
        self.graph.delete_entity(usb_id)
