import logging
import json
from typing import Optional
from friday.providers.vision.base import VisionProvider
from friday.vision.vision_models import DocumentLayout

logger = logging.getLogger(__name__)

class DocumentAnalyzer:
    """Parses documents to extract layout, titles, and key-value pairs."""
    
    def __init__(self, vision_provider: VisionProvider):
        self.vision = vision_provider
        
    async def analyze(self, image_bytes: bytes) -> Optional[DocumentLayout]:
        prompt = (
            "Analyze this document image. Return a JSON object containing: "
            "{\"title\": \"document title\", \"key_value_pairs\": {\"key\": \"value\"}}. "
            "Extract only the most important 5 key-value pairs."
        )
        try:
            response = await self.vision.analyze_image(image_bytes, prompt)
            if response.startswith("```json"):
                response = response.strip("```json").strip("```").strip()
            elif response.startswith("```"):
                response = response.strip("```").strip()
                
            data = json.loads(response)
            
            return DocumentLayout(
                title=data.get("title"),
                key_value_pairs=data.get("key_value_pairs", {})
            )
        except Exception as e:
            logger.error(f"DocumentAnalyzer error: {e}")
            return None
