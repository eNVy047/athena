import time
import httpx
from typing import Dict, Any
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.stt.base import SttProvider

class AzureSpeechSttProvider(SttProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="stt",
            name="azure",
            version="1.0.0",
            capabilities=["speech_to_text"]
        )
        super().__init__(metadata, config)
        self.api_key = config.get("AZURE_SPEECH_KEY", "")
        self.region = config.get("AZURE_SPEECH_REGION", "eastus")
        self.timeout = config.get("PROVIDER_TIMEOUT", 30.0)

    async def initialize(self) -> None:
        if not self.api_key:
            raise ValueError("Azure Speech API Key is required but missing.")

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False

    async def health_check(self) -> bool:
        return bool(self.api_key)

    async def speech_to_text(self, audio_data: bytes) -> str:
        start_time = time.time()
        url = f"https://{self.region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=en-US"
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
            "Accept": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, content=audio_data)
                response.raise_for_status()
                res_json = response.json()
                transcript = res_json.get("DisplayText", "")
                
                latency = (time.time() - start_time) * 1000
                self.health_tracker.record_call(success=True, latency_ms=latency)
                return transcript
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.health_tracker.record_call(success=False, latency_ms=latency, error_msg=str(e))
            raise e
