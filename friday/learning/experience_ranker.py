import logging
from typing import List
from friday.learning.experience_models import Experience

logger = logging.getLogger(__name__)

class ExperienceRanker:
    """Ranks retrieved experiences by relevance, recency, and importance."""
    
    def rank(self, experiences: List[Experience], context_query: str) -> List[Experience]:
        # Simple passthrough for now. Could implement TF-IDF or LLM-based ranking.
        return sorted(experiences, key=lambda e: e.timestamp, reverse=True)
