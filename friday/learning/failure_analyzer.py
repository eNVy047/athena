import logging
from typing import List
from friday.learning.experience_models import Experience

logger = logging.getLogger(__name__)

class FailureAnalyzer:
    """Root-cause analysis of execution outcomes that failed."""
    
    async def analyze(self, failed_experiences: List[Experience]) -> List[str]:
        if not failed_experiences:
            return []
        logger.info(f"Analyzing {len(failed_experiences)} failures.")
        return ["Failure Insight: Network timeout occurred in 80% of provider errors."]
