import time
import httpx
from typing import List, Tuple, Dict, Any
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.reranker.base import RerankerProvider

class CohereRerankerProvider(RerankerProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="reranker",
            name="cohere",
            version="1.0.0",
            capabilities=["rerank"]
        )
        super().__init__(metadata, config)
        self.api_key = config.get("COHERE_API_KEY", "")
        self.model = config.get("RERANKER_MODEL", "rerank-english-v3.0")
        self.timeout = config.get("PROVIDER_TIMEOUT", 30.0)

    async def initialize(self) -> None:
        if not self.api_key:
            raise ValueError("Cohere API Key is required for reranker.")

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False

    async def health_check(self) -> bool:
        return bool(self.api_key)

    async def rerank(self, query: str, documents: List[str], top_n: int = 5) -> List[Tuple[str, float, int]]:
        start_t = time.time()
        url = "https://api.cohere.ai/v1/rerank"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "query": query,
            "documents": documents,
            "top_n": top_n
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                res_json = response.json()
                
                results = []
                for item in res_json.get("results", []):
                    idx = item["index"]
                    results.append((documents[idx], float(item["relevance_score"]), idx))
                    
                self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_t) * 1000)
                return results
        except Exception as e:
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_t) * 1000, error_msg=str(e))
            raise e
