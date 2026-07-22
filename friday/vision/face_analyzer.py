import logging
import json
from typing import List
from friday.providers.vision.base import VisionProvider
from friday.vision.vision_models import VisualEntity

logger = logging.getLogger(__name__)

class FaceAnalyzer:
    """Analyzes faces in the frame using the Vision LLM."""
    
    def __init__(self, vision_provider: VisionProvider):
        self.vision = vision_provider
        
    async def analyze(self, image_bytes: bytes) -> List[VisualEntity]:
        prompt = (
            "Detect and analyze any faces in this image. Return a JSON list. "
            "Format: [{\"label\": \"Person 1\", \"confidence\": 0.9, \"attributes\": {\"expression\": \"smiling\", \"demographics\": \"approx. 30s\"}}]."
        )
        try:
            response = await self.vision.analyze_image(image_bytes, prompt)
            if response.startswith("```json"):
                response = response.strip("```json").strip("```").strip()
            elif response.startswith("```"):
                response = response.strip("```").strip()
                
            data = json.loads(response)
            entities = []
            for item in data:
                entities.append(VisualEntity(
                    label=item.get("label", "face"),
                    confidence=float(item.get("confidence", 0.8)),
                    attributes=item.get("attributes", {})
                ))
            return entities
        except Exception as e:
            logger.error(f"FaceAnalyzer error: {e}")
            return []
