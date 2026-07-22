import time
import math
from typing import List, Tuple
from friday.memory.memory_models import MemoryEntry


class MemoryDecay:
    def __init__(self, forgetting_threshold: float = 1.5):
        self.forgetting_threshold = forgetting_threshold

    def apply_decay(self, entry: MemoryEntry, current_time: float) -> MemoryEntry:
        """Applies Ebbinghaus forgetting curve decay to a memory entry based on time elapsed."""
        time_elapsed = max(0.0, current_time - entry.recency)
        # Convert seconds to hours for standard forgetting rate scaling
        hours_elapsed = time_elapsed / 3600.0

        # Exponential decay formula: S_decayed = S_initial * e^(-decay_rate * hours)
        decayed_importance = entry.importance * math.exp(
            -entry.decay_rate * hours_elapsed
        )

        # Clamp to 0.0 - 10.0 range
        entry.importance = min(10.0, max(0.0, decayed_importance))
        return entry

    def process_decay_and_forget(
        self, entries: List[MemoryEntry]
    ) -> Tuple[List[MemoryEntry], List[MemoryEntry]]:
        """Applies decay to all entries, returning (kept_entries, forgotten_entries)."""
        now = time.time()
        kept = []
        forgotten = []

        for entry in entries:
            decayed_entry = self.apply_decay(entry, now)
            # Retain high-importance or user_profile memories regardless of threshold
            is_essential = (
                decayed_entry.metadata.get("category") == "user_profile"
                or decayed_entry.importance > 8.0
            )

            if decayed_entry.importance >= self.forgetting_threshold or is_essential:
                kept.append(decayed_entry)
            else:
                forgotten.append(decayed_entry)

        return kept, forgotten
