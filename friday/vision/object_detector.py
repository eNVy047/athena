import logging
import json
from typing import List
from friday.providers.vision.base import VisionProvider
from friday.vision.vision_models import VisualEntity

logger = logging.getLogger(__name__)

class ObjectDetector:
    """Detects distinct objects and spatial relationships using Vision LLMs."""
    
    def __init__(self, vision_provider: VisionProvider):
        self.vision = vision_provider
        
    async def detect_objects(self, image_bytes: bytes) -> List[VisualEntity]:
        prompt = (
            "List the primary objects in this image. Return ONLY a JSON list of objects, "
            "each containing: {\"label\": \"name\", \"confidence\": 0.9, \"attributes\": {\"color\": \"red\"}}. "
            "Limit to the 5 most important objects."
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
                    label=item.get("label", "unknown"),
                    confidence=float(item.get("confidence", 0.8)),
                    attributes=item.get("attributes", {})
                ))
            return entities
        except Exception as e:
            logger.error(f"ObjectDetector error: {e}")
            return []
