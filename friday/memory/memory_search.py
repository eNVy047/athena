import math
from typing import List, Tuple
from friday.memory.memory_models import (
    MemoryEntry,
    RetrievedMemory,
    MemorySearchQuery,
    Relationship,
)
from friday.memory.memory_embeddings import MemoryEmbeddingEngine


class MemorySearch:
    def __init__(self, embedding_engine: MemoryEmbeddingEngine):
        self.embedding_engine = embedding_engine

    def keyword_search(
        self, entries: List[MemoryEntry], query: str
    ) -> List[Tuple[MemoryEntry, float]]:
        """Simple TF-IDF/word match keyword search."""
        query_words = set(query.lower().split())
        results = []
        for entry in entries:
            content_words = entry.content.lower().split()
            if not content_words:
                continue
            matches = sum(1 for w in query_words if w in content_words)
            # Normalize match score by query words count
            score = matches / len(query_words) if query_words else 0.0
            results.append((entry, score))
        return sorted(results, key=lambda x: x[1], reverse=True)

    async def embedding_search(
        self, entries: List[MemoryEntry], query: str
    ) -> List[Tuple[MemoryEntry, float]]:
        """Cosine similarity embedding search."""
        query_vector = await self.embedding_engine.get_embedding(query)
        results = []
        for entry in entries:
            if not entry.embedding:
                try:
                    entry.embedding = await self.embedding_engine.get_embedding(
                        entry.content
                    )
                except Exception:
                    results.append((entry, 0.0))
                    continue

            # Cosine similarity
            dot_product = sum(q * d for q, d in zip(query_vector, entry.embedding))
            q_norm = math.sqrt(sum(q * q for q in query_vector))
            d_norm = math.sqrt(sum(d * d for d in entry.embedding))
            similarity = dot_product / (q_norm * d_norm) if q_norm and d_norm else 0.0
            results.append((entry, similarity))
        return sorted(results, key=lambda x: x[1], reverse=True)

    def graph_search(
        self,
        entries: List[MemoryEntry],
        relationships: List[Relationship],
        start_query: str,
    ) -> List[Tuple[MemoryEntry, float]]:
        """Finds related memories by traversing the memory graph (connected entities)."""
        # 1. Start with keyword match to find anchor nodes
        anchors = [
            entry
            for entry, score in self.keyword_search(entries, start_query)
            if score > 0.3
        ]
        if not anchors:
            return []

        anchor_ids = {a.id for a in anchors if a.id}

        # 2. Find neighbors in relationships
        neighbors = set()
        for rel in relationships:
            if rel.source_id in anchor_ids:
                neighbors.add((rel.target_id, rel.weight))
            elif rel.target_id in anchor_ids:
                neighbors.add((rel.source_id, rel.weight))

        # 3. Score entries by proximity to anchors
        scored_entries = []
        entry_map = {e.id: e for e in entries if e.id}

        # Add anchors with weight 1.0
        for a in anchors:
            scored_entries.append((a, 1.0))

        # Add neighbors with relationship weights
        for n_id, weight in neighbors:
            if n_id in entry_map and n_id not in anchor_ids:
                scored_entries.append((entry_map[n_id], weight * 0.7))

        return sorted(scored_entries, key=lambda x: x[1], reverse=True)

    def timeline_search(
        self, entries: List[MemoryEntry], start_time: float, end_time: float
    ) -> List[Tuple[MemoryEntry, float]]:
        """Filters memories chronologically."""
        results = []
        for entry in entries:
            if start_time <= entry.created_at <= end_time:
                # Score based on position in timeline (newer is higher)
                span = max(1.0, end_time - start_time)
                score = (entry.created_at - start_time) / span
                results.append((entry, score))
        return sorted(results, key=lambda x: x[1], reverse=True)

    async def hybrid_search(
        self, entries: List[MemoryEntry], query: MemorySearchQuery
    ) -> List[RetrievedMemory]:
        """Combines keyword and embedding searches using hybrid weights."""
        if not entries:
            return []

        # 1. Run keyword search
        kw_results = {
            entry.id: score
            for entry, score in self.keyword_search(entries, query.query)
        }

        # 2. Run embedding search
        emb_results = {
            entry.id: score
            for entry, score in await self.embedding_search(entries, query.query)
        }

        # 3. Combine scores
        combined = []
        for entry in entries:
            kw_score = kw_results.get(entry.id, 0.0)
            emb_score = emb_results.get(entry.id, 0.0)

            hybrid_score = (query.hybrid_weight * kw_score) + (
                (1 - query.hybrid_weight) * emb_score
            )

            if hybrid_score >= query.min_score:
                combined.append(RetrievedMemory(entry=entry, score=hybrid_score))

        combined.sort(key=lambda x: x.score, reverse=True)
        return combined[: query.limit]
