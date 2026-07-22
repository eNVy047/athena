from abc import abstractmethod
from friday.providers.base.provider import Provider

class OcrProvider(Provider):
    @abstractmethod
    async def extract_text(self, image_bytes: bytes) -> str:
        """Extracts text from image bytes."""
        pass
