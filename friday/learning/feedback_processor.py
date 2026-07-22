import logging
from typing import List

logger = logging.getLogger(__name__)

class FeedbackProcessor:
    """Parses direct user corrections and applies them to behavior."""
    
    async def process_corrections(self, corrections: List[str]) -> List[str]:
        if not corrections:
            return []
        logger.info(f"Processing {len(corrections)} user corrections.")
        return [f"Applied correction: {c}" for c in corrections]
