from typing import List, Dict, Any, Optional
from friday.world.knowledge_graph import KnowledgeGraph
from friday.world.entity import WorldEntity
from friday.world.ontology import EntityType

class LocationManager:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.graph = knowledge_graph

    def add_location(self, location_id: str, name: str, properties: Optional[Dict[str, Any]] = None) -> WorldEntity:
        props = properties or {}
        props.update({"name": name})
        entity = WorldEntity(location_id, EntityType.LOCATION, props)
        self.graph.add_entity(entity)
        return entity

    def get_location(self, location_id: str) -> Optional[WorldEntity]:
        entity = self.graph.get_entity(location_id)
        if entity and entity.type == EntityType.LOCATION:
            return entity
        return None

    def list_locations(self) -> List[WorldEntity]:
        return self.graph.list_entities(EntityType.LOCATION)

    def remove_location(self, location_id: str) -> None:
        loc = self.get_location(location_id)
        if loc:
            self.graph.delete_entity(location_id)
