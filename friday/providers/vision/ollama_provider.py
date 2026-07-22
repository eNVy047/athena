import time
import httpx
import base64
from typing import Dict, Any
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.vision.base import VisionProvider

class OllamaVisionProvider(VisionProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="vision",
            name="ollama",
            version="1.0.0",
            capabilities=["analyze_image"]
        )
        super().__init__(metadata, config)
        self.host = config.get("OLLAMA_HOST", "http://localhost:11434")
        self.model = config.get("VISION_MODEL", "llava")
        self.timeout = config.get("PROVIDER_TIMEOUT", 30.0)

    async def initialize(self) -> None:
        pass

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{self.host}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    async def analyze_image(self, image_bytes: bytes, prompt: str) -> Dict[str, Any]:
        start_time = time.time()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        url = f"{self.host}/api/generate"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": self.model,
            "prompt": prompt,
            "images": [base64_image],
            "stream": False
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                res_json = response.json()
                content = res_json["response"]
                
                latency = (time.time() - start_time) * 1000
                self.health_tracker.record_call(success=True, latency_ms=latency)
                return {"provider": "ollama", "status": "success", "result": content}
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.health_tracker.record_call(success=False, latency_ms=latency, error_msg=str(e))
            raise e
