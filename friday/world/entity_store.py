from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from friday.world.entity import WorldEntity
from friday.world.ontology import EntityType

class EntityStoreProvider(ABC):
    @abstractmethod
    def save(self, entity: WorldEntity) -> None:
        pass

    @abstractmethod
    def get(self, entity_id: str) -> Optional[WorldEntity]:
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> None:
        pass

    @abstractmethod
    def list_all(self, entity_type: Optional[EntityType] = None) -> List[WorldEntity]:
        pass

class InMemoryEntityStoreProvider(EntityStoreProvider):
    def __init__(self):
        self._entities: Dict[str, WorldEntity] = {}

    def save(self, entity: WorldEntity) -> None:
        self._entities[entity.id] = entity

    def get(self, entity_id: str) -> Optional[WorldEntity]:
        return self._entities.get(entity_id)

    def delete(self, entity_id: str) -> None:
        if entity_id in self._entities:
            del self._entities[entity_id]

    def list_all(self, entity_type: Optional[EntityType] = None) -> List[WorldEntity]:
        if entity_type is None:
            return list(self._entities.values())
        return [e for e in self._entities.values() if e.type == entity_type]
