from typing import List, Dict, Set, Optional, Tuple
from friday.world.entity import WorldEntity
from friday.world.relationship import Relationship
from friday.world.ontology import EntityType, RelationshipType
from friday.world.entity_store import EntityStoreProvider
from friday.world.relationship_graph import RelationshipStoreProvider

class KnowledgeGraph:
    def __init__(self, entity_store: EntityStoreProvider, relationship_graph: RelationshipStoreProvider):
        self.entity_store = entity_store
        self.relationship_graph = relationship_graph

    def add_entity(self, entity: WorldEntity) -> None:
        self.entity_store.save(entity)

    def get_entity(self, entity_id: str) -> Optional[WorldEntity]:
        return self.entity_store.get(entity_id)

    def delete_entity(self, entity_id: str) -> None:
        self.entity_store.delete(entity_id)
        # Also clean up relationships associated with this entity
        outgoing = self.relationship_graph.get_relationships(source_id=entity_id)
        for r in outgoing:
            self.relationship_graph.remove_relationship(r.source_id, r.target_id, r.relation_type)
        incoming = self.relationship_graph.get_relationships(target_id=entity_id)
        for r in incoming:
            self.relationship_graph.remove_relationship(r.source_id, r.target_id, r.relation_type)

    def list_entities(self, entity_type: Optional[EntityType] = None) -> List[WorldEntity]:
        return self.entity_store.list_all(entity_type)

    def add_relationship(self, relationship: Relationship) -> None:
        # Verify source and target exist
        if not self.entity_store.get(relationship.source_id):
            raise ValueError(f"Source entity {relationship.source_id} does not exist.")
        if not self.entity_store.get(relationship.target_id):
            raise ValueError(f"Target entity {relationship.target_id} does not exist.")
        self.relationship_graph.add_relationship(relationship)

    def remove_relationship(self, source_id: str, target_id: str, relation_type: RelationshipType) -> None:
        self.relationship_graph.remove_relationship(source_id, target_id, relation_type)

    def get_relationships(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relation_type: Optional[RelationshipType] = None
    ) -> List[Relationship]:
        return self.relationship_graph.get_relationships(source_id, target_id, relation_type)

    def get_neighbors(self, entity_id: str) -> List[Tuple[str, RelationshipType, str]]:
        """Returns List of (neighbor_id, relation_type, direction) where direction is 'out' or 'in'."""
        neighbors = []
        outgoing = self.relationship_graph.get_relationships(source_id=entity_id)
        for r in outgoing:
            neighbors.append((r.target_id, r.relation_type, "out"))
        incoming = self.relationship_graph.get_relationships(target_id=entity_id)
        for r in incoming:
            neighbors.append((r.source_id, r.relation_type, "in"))
        return neighbors

    def find_shortest_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """Finds shortest path using BFS. Returns list of entity IDs from source to target."""
        if source_id == target_id:
            return [source_id]

        visited = {source_id}
        queue = [[source_id]]

        while queue:
            path = queue.pop(0)
            node = path[-1]

            # Get neighbors (only outgoing and incoming edges can be followed)
            for neighbor_id, _, _ in self.get_neighbors(node):
                if neighbor_id == target_id:
                    return path + [neighbor_id]
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append(path + [neighbor_id])
        return None
