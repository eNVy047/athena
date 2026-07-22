import time
import httpx
import base64
from typing import Dict, Any
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.vision.base import VisionProvider

class GeminiVisionProvider(VisionProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="vision",
            name="gemini",
            version="1.0.0",
            capabilities=["analyze_image"]
        )
        super().__init__(metadata, config)
        self.api_key = config.get("GEMINI_API_KEY", "")
        self.model = config.get("VISION_MODEL", "gemini-2.5-flash")
        self.timeout = config.get("PROVIDER_TIMEOUT", 30.0)

    async def initialize(self) -> None:
        if not self.api_key:
            raise ValueError("Gemini API Key is required but missing.")

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False

    async def health_check(self) -> bool:
        return bool(self.api_key)

    async def analyze_image(self, image_bytes: bytes, prompt: str) -> Dict[str, Any]:
        start_time = time.time()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        # Gemini inlineData structure
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inlineData": {
                                "mimeType": "image/jpeg",
                                "data": base64_image
                            }
                        }
                    ]
                }
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                res_json = response.json()
                content = res_json["candidates"][0]["content"]["parts"][0]["text"]
                
                latency = (time.time() - start_time) * 1000
                self.health_tracker.record_call(success=True, latency_ms=latency)
                return {"provider": "gemini", "status": "success", "result": content}
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.health_tracker.record_call(success=False, latency_ms=latency, error_msg=str(e))
            raise e
