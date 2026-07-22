import logging
from typing import List
from friday.learning.experience_store import ExperienceStore

logger = logging.getLogger(__name__)

class HabitDetector:
    """Detects user routines and daily habits."""
    
    def __init__(self, store: ExperienceStore):
        self.store = store
        
    async def detect_habits(self) -> List[str]:
        logger.info("Detecting user habits.")
        # Mock habit detection
        return ["Habit: Starts day by reading HackerNews."]
