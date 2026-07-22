import logging
import json
from typing import Optional
from friday.providers.vision.base import VisionProvider
from friday.vision.vision_models import SceneUnderstanding

logger = logging.getLogger(__name__)

class SceneAnalyzer:
    """Analyzes the global context and environment of an image."""
    
    def __init__(self, vision_provider: VisionProvider):
        self.vision = vision_provider
        
    async def analyze(self, image_bytes: bytes) -> Optional[SceneUnderstanding]:
        prompt = (
            "Analyze this scene. Return ONLY a JSON object with this exact structure: "
            "{\"description\": \"detailed summary\", \"environment_type\": \"indoor/outdoor/desktop/etc\", "
            "\"lighting_conditions\": \"bright/dark/etc\", \"key_objects\": [\"list\"], \"detected_activities\": [\"list\"]}"
        )
        try:
            response = await self.vision.analyze_image(image_bytes, prompt)
            
            # Clean markdown formatting if present
            if response.startswith("```json"):
                response = response.strip("```json").strip("```").strip()
            elif response.startswith("```"):
                response = response.strip("```").strip()
                
            data = json.loads(response)
            return SceneUnderstanding(
                description=data.get("description", ""),
                environment_type=data.get("environment_type"),
                lighting_conditions=data.get("lighting_conditions"),
                key_objects=data.get("key_objects", []),
                detected_activities=data.get("detected_activities", [])
            )
        except Exception as e:
            logger.error(f"SceneAnalyzer error: {e}")
            return None
