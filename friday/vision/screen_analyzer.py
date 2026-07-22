import logging
import json
from typing import List
from friday.providers.vision.base import VisionProvider
from friday.vision.vision_models import VisualEntity

logger = logging.getLogger(__name__)

class ScreenAnalyzer:
    """Analyzes UI elements on desktop or browser screenshots."""
    
    def __init__(self, vision_provider: VisionProvider):
        self.vision = vision_provider
        
    async def analyze(self, image_bytes: bytes) -> List[VisualEntity]:
        prompt = (
            "Analyze this computer screen. Return a JSON list of the primary UI elements (buttons, menus, windows). "
            "Format: [{\"label\": \"Submit Button\", \"confidence\": 0.9, \"attributes\": {\"type\": \"button\"}}]."
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
                    label=item.get("label", "unknown_ui"),
                    confidence=float(item.get("confidence", 0.8)),
                    attributes=item.get("attributes", {})
                ))
            return entities
        except Exception as e:
            logger.error(f"ScreenAnalyzer error: {e}")
            return []
