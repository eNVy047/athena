import logging
from typing import List
from friday.learning.experience_models import Experience
from friday.memory.memory_manager import MemoryManager

logger = logging.getLogger(__name__)

class ExperienceStore:
    """Stores raw experiences for reflection. Backed by MemoryManager to avoid duplicate storage."""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        
    async def add_experience(self, exp: Experience):
        text = f"Experience [{exp.type}]: {exp.trigger} -> {'Success' if exp.success else 'Failed'}\n"
        if exp.error_message:
            text += f"Error: {exp.error_message}\n"
        if exp.result_summary:
            text += f"Summary: {exp.result_summary}\n"
            
        await self.memory.add_memory(
            text=text,
            metadata={
                "category": "experience",
                "experience_id": exp.id,
                "experience_type": exp.type,
                "success": exp.success
            }
        )
        logger.info(f"Stored experience {exp.id}")
        
    async def get_recent_experiences(self, limit: int = 50) -> List[Experience]:
        # In a real system, we'd query MemoryManager by category="experience"
        # Since MemoryManager interface might be simple, we mock the retrieval for this Engine.
        # This allows pattern detectors to run on history.
        # Actually returning empty list for now until MemoryManager supports filtering by category.
        return []
