import logging
import time
from typing import List, Tuple
from friday.memory.memory_models import MemoryEntry, MemoryType
from friday.memory.memory_search import MemorySearch

logger = logging.getLogger("friday-agent")


class MemoryConsolidation:
    def __init__(self, search_engine: MemorySearch, similarity_threshold: float = 0.85):
        self.search_engine = search_engine
        self.similarity_threshold = similarity_threshold

    async def consolidate(
        self, entries: List[MemoryEntry]
    ) -> Tuple[List[MemoryEntry], List[str]]:
        """Consolidates short-term/episodic memories.

        Merges duplicates and upgrades high-importance entries to semantic/long-term memory.
        Returns (updated_or_new_entries, ids_to_delete).
        """
        short_term = [
            e
            for e in entries
            if e.memory_type in (MemoryType.SHORT_TERM, MemoryType.EPISODIC)
        ]
        if len(short_term) < 2:
            return [], []

        to_delete = []
        consolidated = []
        processed_ids = set()

        for i, entry in enumerate(short_term):
            if entry.id in processed_ids or entry.id in to_delete:
                continue

            # Find similar memories
            similar = []
            for other in short_term[i + 1 :]:
                if other.id in processed_ids or other.id in to_delete:
                    continue
                # Cosine similarity using search engine
                sim_score = 0.0
                if entry.embedding and other.embedding:
                    import math

                    dot_product = sum(
                        q * d for q, d in zip(entry.embedding, other.embedding)
                    )
                    q_norm = math.sqrt(sum(q * q for q in entry.embedding))
                    d_norm = math.sqrt(sum(d * d for d in other.embedding))
                    sim_score = (
                        dot_product / (q_norm * d_norm) if q_norm and d_norm else 0.0
                    )

                if sim_score >= self.similarity_threshold:
                    similar.append(other)

            if similar:
                # Merge duplicate memories into the first one
                logger.info(
                    f"[Consolidation] Merging {len(similar)} similar memories into entry: {entry.id}"
                )
                merged_content = entry.content
                # Collect unique metadata
                merged_metadata = dict(entry.metadata)
                for item in similar:
                    to_delete.append(item.id)
                    merged_metadata.update(item.metadata)

                entry.content = merged_content
                entry.metadata = merged_metadata
                entry.importance = min(
                    10.0,
                    max(entry.importance, *(item.importance for item in similar)) + 0.5,
                )
                entry.recency = time.time()

            # If the entry has high importance, promote it to SEMANTIC / LONG_TERM memory
            if entry.importance >= 6.5:
                entry.memory_type = MemoryType.SEMANTIC
                logger.info(
                    f"[Consolidation] Promoting entry {entry.id} to Semantic Memory."
                )

            consolidated.append(entry)
            processed_ids.add(entry.id)

        return consolidated, to_delete
