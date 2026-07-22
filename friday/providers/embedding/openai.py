import time
import httpx
from typing import List, Dict, Any
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.embedding.base import EmbeddingProvider

class OpenAiEmbeddingProvider(EmbeddingProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="embedding",
            name="openai",
            version="1.0.0",
            capabilities=["get_embedding", "get_embeddings"]
        )
        super().__init__(metadata, config)
        self.api_key = config.get("OPENAI_API_KEY", "")
        self.model = config.get("EMBEDDING_MODEL", "text-embedding-3-small")
        self.timeout = config.get("PROVIDER_TIMEOUT", 30.0)

    async def initialize(self) -> None:
        if not self.api_key:
            raise ValueError("OpenAI API Key is required for OpenAI Embeddings.")

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False

    async def health_check(self) -> bool:
        return bool(self.api_key)

    async def get_embedding(self, text: str) -> List[float]:
        res = await self.get_embeddings([text])
        return res[0]

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        start_time = time.time()
        url = "https://api.openai.com/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "input": texts,
            "model": self.model
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                res_json = response.json()
                embeddings = [item["embedding"] for item in res_json["data"]]
                
                latency = (time.time() - start_time) * 1000
                self.health_tracker.record_call(success=True, latency_ms=latency)
                return embeddings
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.health_tracker.record_call(success=False, latency_ms=latency, error_msg=str(e))
            raise e
