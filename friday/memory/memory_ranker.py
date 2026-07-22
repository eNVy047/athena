import time
from typing import List
from friday.memory.memory_models import RetrievedMemory


class MemoryRanker:
    def __init__(
        self,
        recency_weight: float = 0.3,
        relevance_weight: float = 0.5,
        importance_weight: float = 0.2,
    ):
        self.recency_weight = recency_weight
        self.relevance_weight = relevance_weight
        self.importance_weight = importance_weight

    def rank(self, retrieved: List[RetrievedMemory]) -> List[RetrievedMemory]:
        """Ranks memory entries based on combined score: relevance, importance, and recency."""
        if not retrieved:
            return []

        now = time.time()

        # 1. Normalize recency (newer is higher)
        max_age = 1.0
        ages = []
        for r in retrieved:
            age = max(0.0, now - r.entry.recency)
            ages.append(age)
            if age > max_age:
                max_age = age

        ranked_list = []
        for i, r in enumerate(retrieved):
            # Recency score: 1.0 at now, decaying to 0.0 at max_age
            recency_score = 1.0 - (ages[i] / max_age) if max_age > 0 else 1.0

            # Importance score (normalized from 0.0-10.0 range to 0.0-1.0)
            importance_score = min(1.0, max(0.0, r.entry.importance / 10.0))

            # Relevance score is already in r.score (usually 0.0 to 1.0)
            relevance_score = r.score

            combined_score = (
                (self.recency_weight * recency_score)
                + (self.relevance_weight * relevance_score)
                + (self.importance_weight * importance_score)
            )

            # Update score
            r.score = combined_score
            ranked_list.append(r)

        return sorted(ranked_list, key=lambda x: x.score, reverse=True)
