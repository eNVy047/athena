import time
import httpx
from typing import List, Dict, Any
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.search.base import SearchProvider

class SerperSearchProvider(SearchProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="search",
            name="serper",
            version="1.0.0",
            capabilities=["search"]
        )
        super().__init__(metadata, config)
        self.api_key = config.get("SERPER_API_KEY", "")
        self.timeout = config.get("PROVIDER_TIMEOUT", 30.0)

    async def initialize(self) -> None:
        if not self.api_key:
            raise ValueError("Serper API Key is required but missing.")

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False

    async def health_check(self) -> bool:
        return bool(self.api_key)

    async def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        start_time = time.time()
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        data = {"q": query, "num": num_results}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                res_json = response.json()
                
                results = []
                for item in res_json.get("organic", []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "content": item.get("snippet", ""),
                        "raw": item
                    })
                
                self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_time) * 1000)
                return results
        except Exception as e:
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_time) * 1000, error_msg=str(e))
            raise e
