import time
from typing import Dict, Any, Optional
from friday.world.ontology import EntityType

class WorldEntity:
    def __init__(
        self,
        entity_id: str,
        entity_type: EntityType,
        properties: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = entity_id
        self.type = entity_type
        self.properties = properties or {}
        self.metadata = metadata or {}
        
        # Enforce lifecycle timestamps
        now = time.time()
        if "created_at" not in self.metadata:
            self.metadata["created_at"] = now
        if "updated_at" not in self.metadata:
            self.metadata["updated_at"] = now

    def update_property(self, key: str, value: Any) -> None:
        self.properties[key] = value
        self.metadata["updated_at"] = time.time()

    def get_property(self, key: str, default: Any = None) -> Any:
        return self.properties.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value if isinstance(self.type, EntityType) else self.type,
            "properties": self.properties,
            "metadata": self.metadata
        }
