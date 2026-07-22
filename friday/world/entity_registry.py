from typing import Set
from friday.world.ontology import EntityType
from friday.world.entity import WorldEntity

class EntityRegistry:
    def __init__(self):
        self._registered_types: Set[EntityType] = set(EntityType)

    def register_entity_type(self, entity_type: EntityType) -> None:
        self._registered_types.add(entity_type)

    def is_valid_type(self, entity_type: EntityType) -> bool:
        return entity_type in self._registered_types

    def validate_entity(self, entity: WorldEntity) -> bool:
        if not entity.id or not isinstance(entity.id, str):
            return False
        if not self.is_valid_type(entity.type):
            return False
        return True
