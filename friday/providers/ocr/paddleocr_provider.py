import logging
import time
from typing import Dict, Any
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.ocr.base import OcrProvider

logger = logging.getLogger(__name__)

class PaddleOcrProvider(OcrProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="ocr",
            name="paddleocr",
            version="1.0.0",
            capabilities=["extract_text"]
        )
        super().__init__(metadata, config)
        self._ocr = None

    async def initialize(self) -> None:
        try:
            from paddleocr import PaddleOCR
            self._ocr = PaddleOCR(use_angle_cls=True, lang='en')
        except Exception as e:
            logger.warning(f"PaddleOCR reader initialization deferred: {e}")

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False
        self._ocr = None

    async def health_check(self) -> bool:
        try:
            from paddleocr import PaddleOCR
            return True
        except ImportError:
            return False

    async def extract_text(self, image_bytes: bytes) -> str:
        start_time = time.time()
        try:
            if not self._ocr:
                from paddleocr import PaddleOCR
                self._ocr = PaddleOCR(use_angle_cls=True, lang='en')
            
            result = self._ocr.ocr(image_bytes, cls=True)
            texts = []
            for idx in range(len(result)):
                res = result[idx]
                if res:
                    for line in res:
                        texts.append(line[1][0])
            text = " ".join(texts)
            
            latency = (time.time() - start_time) * 1000
            self.health_tracker.record_call(success=True, latency_ms=latency)
            return text
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.health_tracker.record_call(success=False, latency_ms=latency, error_msg=str(e))
            raise e
