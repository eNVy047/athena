import logging
import time
from typing import Dict, Any
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.ocr.base import OcrProvider

logger = logging.getLogger(__name__)

class EasyOcrProvider(OcrProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="ocr",
            name="easyocr",
            version="1.0.0",
            capabilities=["extract_text"]
        )
        super().__init__(metadata, config)
        self._reader = None

    async def initialize(self) -> None:
        try:
            import easyocr
            self._reader = easyocr.Reader(['en'])
        except Exception as e:
            logger.warning(f"EasyOCR reader initialization deferred: {e}")

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False
        self._reader = None

    async def health_check(self) -> bool:
        try:
            import easyocr
            return True
        except ImportError:
            return False

    async def extract_text(self, image_bytes: bytes) -> str:
        start_time = time.time()
        try:
            if not self._reader:
                import easyocr
                self._reader = easyocr.Reader(['en'])
            
            # Run extraction
            results = self._reader.readtext(image_bytes)
            text = " ".join([res[1] for res in results])
            
            latency = (time.time() - start_time) * 1000
            self.health_tracker.record_call(success=True, latency_ms=latency)
            return text
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.health_tracker.record_call(success=False, latency_ms=latency, error_msg=str(e))
            raise e
