import logging
from typing import Optional
from friday.providers.ocr.base import OcrProvider

logger = logging.getLogger(__name__)

class TextReader:
    """Uses OCR Providers to extract raw text and bounding boxes from images."""
    
    def __init__(self, ocr_provider: OcrProvider):
        self.ocr_provider = ocr_provider
        
    async def extract_text(self, image_bytes: bytes) -> Optional[str]:
        try:
            return await self.ocr_provider.extract_text(image_bytes)
        except Exception as e:
            logger.error(f"TextReader error: {e}")
            return None
