from abc import ABC, abstractmethod
from typing import List, Dict, Set, Optional
from friday.world.relationship import Relationship
from friday.world.ontology import RelationshipType

class RelationshipStoreProvider(ABC):
    @abstractmethod
    def add_relationship(self, relationship: Relationship) -> None:
        pass

    @abstractmethod
    def remove_relationship(self, source_id: str, target_id: str, relation_type: RelationshipType) -> None:
        pass

    @abstractmethod
    def get_relationships(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relation_type: Optional[RelationshipType] = None
    ) -> List[Relationship]:
        pass

class InMemoryRelationshipStoreProvider(RelationshipStoreProvider):
    def __init__(self):
        self._relationships: List[Relationship] = []

    def add_relationship(self, relationship: Relationship) -> None:
        # Avoid duplicate exact relationships
        for r in self._relationships:
            if (r.source_id == relationship.source_id and 
                r.target_id == relationship.target_id and 
                r.relation_type == relationship.relation_type):
                r.properties.update(relationship.properties)
                r.metadata.update(relationship.metadata)
                return
        self._relationships.append(relationship)

    def remove_relationship(self, source_id: str, target_id: str, relation_type: RelationshipType) -> None:
        self._relationships = [
            r for r in self._relationships
            if not (r.source_id == source_id and r.target_id == target_id and r.relation_type == relation_type)
        ]

    def get_relationships(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relation_type: Optional[RelationshipType] = None
    ) -> List[Relationship]:
        res = self._relationships
        if source_id is not None:
            res = [r for r in res if r.source_id == source_id]
        if target_id is not None:
            res = [r for r in res if r.target_id == target_id]
        if relation_type is not None:
            res = [r for r in res if r.relation_type == relation_type]
        return res
