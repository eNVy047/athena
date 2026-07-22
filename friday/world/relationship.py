import time
from typing import Dict, Any, Optional
from friday.world.ontology import RelationshipType

class Relationship:
    def __init__(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationshipType,
        properties: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type
        self.properties = properties or {}
        self.metadata = metadata or {}

        now = time.time()
        if "created_at" not in self.metadata:
            self.metadata["created_at"] = now
        if "updated_at" not in self.metadata:
            self.metadata["updated_at"] = now

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type.value if isinstance(self.relation_type, RelationshipType) else self.relation_type,
            "properties": self.properties,
            "metadata": self.metadata
        }
