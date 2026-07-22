import json
from pathlib import Path
from friday.memory.memory_models import MemoryEntry, Relationship


class MemorySnapshotManager:
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager

    def create_snapshot(self, target_filepath: str) -> None:
        """Serializes current memory store state (entries and relationships) to a file."""
        entries = self.memory_manager.router.retrieve_all()
        relationships = []
        if hasattr(self.memory_manager.router.stores[0], "get_relationships"):
            relationships = self.memory_manager.router.stores[0].get_relationships()

        snapshot_data = {
            "entries": [e.dict() for e in entries],
            "relationships": [r.dict() for r in relationships],
        }

        path = Path(target_filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(snapshot_data, indent=2), encoding="utf-8")

    async def restore_snapshot(self, source_filepath: str) -> None:
        """Restores memory store state from a snapshot file."""
        path = Path(source_filepath)
        if not path.exists():
            return

        snapshot_data = json.loads(path.read_text(encoding="utf-8"))

        # Clear existing memories
        self.memory_manager.router.stores[0].clear()

        # Restore entries
        for entry_dict in snapshot_data.get("entries", []):
            entry_dict.pop("embedding", None)  # Re-compute or reload
            entry = MemoryEntry(**entry_dict)
            await self.memory_manager.store_memory(entry)

        # Restore relationships
        for rel_dict in snapshot_data.get("relationships", []):
            rel = Relationship(**rel_dict)
            self.memory_manager.router.stores[0].add_relationship(rel)
