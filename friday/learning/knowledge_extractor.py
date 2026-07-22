import logging
from typing import List
from friday.learning.experience_models import Experience

logger = logging.getLogger(__name__)

class KnowledgeExtractor:
    """Distills raw logs into abstract semantic knowledge."""
    
    async def extract_knowledge(self, experiences: List[Experience]) -> List[str]:
        if not experiences:
            return []
        logger.info(f"Extracting knowledge from {len(experiences)} experiences.")
        return ["Fact: User prefers using pip over conda."]
