import logging
from typing import List
from friday.providers.llm.base import LlmProvider
from friday.learning.experience_models import Experience
from friday.learning.experience_store import ExperienceStore

logger = logging.getLogger(__name__)

class ReflectionEngine:
    """Evaluates what worked, what failed, and generates optimization reports."""
    
    def __init__(self, llm_provider: LlmProvider, store: ExperienceStore):
        self.llm = llm_provider
        self.store = store
        
    async def reflect_on_experiences(self, experiences: List[Experience]) -> List[str]:
        if not experiences:
            return []
            
        logger.info(f"Reflecting on {len(experiences)} recent experiences.")
        # In a real implementation, we would build a prompt with the experiences and ask the LLM to extract lessons.
        try:
            # Mocking the call for brevity
            # response = await self.llm.generate(prompt)
            return ["Lesson 1: Always verify file paths.", "Lesson 2: Retry network calls."]
        except Exception as e:
            logger.error(f"ReflectionEngine error: {e}")
            return []
