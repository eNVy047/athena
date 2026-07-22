from typing import List, Dict, Any, Optional
from friday.world.knowledge_graph import KnowledgeGraph
from friday.world.entity import WorldEntity
from friday.world.ontology import EntityType

class PeopleManager:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.graph = knowledge_graph

    def add_person(self, person_id: str, name: str, email: Optional[str] = None, properties: Optional[Dict[str, Any]] = None) -> WorldEntity:
        props = properties or {}
        props.update({"name": name})
        if email:
            props["email"] = email
        entity = WorldEntity(person_id, EntityType.PERSON, props)
        self.graph.add_entity(entity)
        return entity

    def get_person(self, person_id: str) -> Optional[WorldEntity]:
        entity = self.graph.get_entity(person_id)
        if entity and entity.type == EntityType.PERSON:
            return entity
        return None

    def list_people(self) -> List[WorldEntity]:
        return self.graph.list_entities(EntityType.PERSON)

    def remove_person(self, person_id: str) -> None:
        person = self.get_person(person_id)
        if person:
            self.graph.delete_entity(person_id)
