from abc import abstractmethod
from typing import Dict, Any
from friday.providers.base.provider import Provider

class VisionProvider(Provider):
    @abstractmethod
    async def analyze_image(self, image_bytes: bytes, prompt: str) -> Dict[str, Any]:
        """Analyzes an image and returns findings."""
        pass
