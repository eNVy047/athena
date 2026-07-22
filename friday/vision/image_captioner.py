import logging
from typing import Optional
from friday.providers.vision.base import VisionProvider

logger = logging.getLogger(__name__)

class ImageCaptioner:
    """Generates a high-level descriptive caption of an image."""
    
    def __init__(self, vision_provider: VisionProvider):
        self.vision = vision_provider
        
    async def generate_caption(self, image_bytes: bytes) -> Optional[str]:
        prompt = "Provide a concise, single-sentence caption describing this image."
        try:
            response = await self.vision.analyze_image(image_bytes, prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"ImageCaptioner error: {e}")
            return None
