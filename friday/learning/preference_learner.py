import logging
from typing import Dict, Any
from friday.learning.experience_store import ExperienceStore

logger = logging.getLogger(__name__)

class PreferenceLearner:
    """Infers user preferences without overwriting explicit ones."""
    
    def __init__(self, store: ExperienceStore):
        self.store = store
        
    async def learn_preferences(self) -> Dict[str, Any]:
        logger.info("Learning implicit preferences.")
        # Mock preference inference
        return {"preferred_editor": "vscode", "preferred_shell": "zsh"}
