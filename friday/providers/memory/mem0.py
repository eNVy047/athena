import time
import httpx
from typing import List, Dict, Any, Optional
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.memory.base import MemoryProvider

class Mem0MemoryProvider(MemoryProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="memory",
            name="mem0",
            version="1.0.0",
            capabilities=["add", "search", "delete"]
        )
        super().__init__(metadata, config)
        self.api_key = config.get("MEM0_API_KEY", "")
        self.timeout = config.get("PROVIDER_TIMEOUT", 30.0)

    async def initialize(self) -> None:
        if not self.api_key:
            raise ValueError("Mem0 API Key is required but missing.")

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False

    async def health_check(self) -> bool:
        return bool(self.api_key)

    async def add(self, text: str, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        start_time = time.time()
        url = "https://api.mem0.ai/v1/memories/"
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "messages": [{"role": "user", "content": text}],
            "user_id": user_id,
            "metadata": metadata or {}
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_time) * 1000)
        except Exception as e:
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_time) * 1000, error_msg=str(e))
            raise e

    async def search(self, query: str, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        start_time = time.time()
        url = "https://api.mem0.ai/v1/memories/search/"
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "query": query,
            "user_id": user_id,
            "limit": limit
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                res_json = response.json()
                
                self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_time) * 1000)
                # Formats the response to structured list of memories
                return res_json
        except Exception as e:
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_time) * 1000, error_msg=str(e))
            raise e

    async def delete(self, memory_id: str) -> None:
        start_time = time.time()
        url = f"https://api.mem0.ai/v1/memories/{memory_id}/"
        headers = {
            "Authorization": f"Token {self.api_key}"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(url, headers=headers)
                response.raise_for_status()
                self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_time) * 1000)
        except Exception as e:
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_time) * 1000, error_msg=str(e))
            raise e
