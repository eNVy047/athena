from typing import List
from friday.memory.memory_models import MemoryEntry, MemoryType


class MemoryTimeline:
    def get_chronological_sequence(
        self, entries: List[MemoryEntry], limit: int = 20
    ) -> List[MemoryEntry]:
        """Gets sequential conversation or episodic memories sorted chronologically."""
        seq_types = {MemoryType.CONVERSATION, MemoryType.EPISODIC}
        filtered = [e for e in entries if e.memory_type in seq_types]
        return sorted(filtered, key=lambda x: x.created_at, reverse=True)[:limit]
