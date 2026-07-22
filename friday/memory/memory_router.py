from typing import List, Optional
from friday.memory.memory_models import MemoryEntry, MemoryType
from friday.memory.memory_store import MemoryStore


class MemoryRouter:
    def __init__(self, stores: List[MemoryStore]):
        self.stores = stores

    def route_store(self, entry: MemoryEntry) -> None:
        """Routes a memory entry to all registered swappable storage providers."""
        for store in self.stores:
            store.add_memory(entry)

    def route_delete(self, memory_id: str) -> None:
        """Deletes a memory entry across all registered storage providers."""
        for store in self.stores:
            store.delete_memory(memory_id)

    def retrieve_all(
        self, memory_types: Optional[List[MemoryType]] = None
    ) -> List[MemoryEntry]:
        """Collects memories from the primary store (using the first swappable store as source of truth)."""
        if not self.stores:
            return []
        return self.stores[0].get_memories(memory_types)
