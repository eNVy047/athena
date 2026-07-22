import time
import httpx
from typing import Dict, Any, AsyncIterator
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.tts.base import TtsProvider

class DeepgramTtsProvider(TtsProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="tts",
            name="deepgram",
            version="1.0.0",
            capabilities=["text_to_speech"]
        )
        super().__init__(metadata, config)
        self.api_key = config.get("DEEPGRAM_API_KEY", "")
        self.timeout = config.get("PROVIDER_TIMEOUT", 30.0)

    async def initialize(self) -> None:
        if not self.api_key:
            raise ValueError("Deepgram API Key is required but missing.")

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False

    async def health_check(self) -> bool:
        return bool(self.api_key)

    async def text_to_speech(self, text: str) -> AsyncIterator[bytes]:
        url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {"text": text}
        
        async def stream_generator():
            start_time = time.time()
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    async with client.stream("POST", url, headers=headers, json=data) as response:
                        response.raise_for_status()
                        async for chunk in response.aiter_bytes(chunk_size=4096):
                            yield chunk
                self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_time) * 1000)
            except Exception as e:
                self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_time) * 1000, error_msg=str(e))
                raise e

        return stream_generator()
