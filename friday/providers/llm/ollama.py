import time
import httpx
from typing import List, Dict, Any, AsyncIterator
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.llm.base import LlmProvider, LLMMessage, LLMResponse

class OllamaLlmProvider(LlmProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="llm",
            name="ollama",
            version="1.0.0",
            capabilities=["chat", "chat_stream"]
        )
        super().__init__(metadata, config)
        self.host = config.get("OLLAMA_HOST", "http://localhost:11434")
        self.model = config.get("LLM_MODEL", "llama3")
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

    async def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        start_time = time.time()
        url = f"{self.host}/api/chat"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            **kwargs
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                res_json = response.json()
                content = res_json["message"]["content"]
                
                latency = (time.time() - start_time) * 1000
                self.health_tracker.record_call(success=True, latency_ms=latency)
                return LLMResponse(content=content, raw_response=res_json)
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.health_tracker.record_call(success=False, latency_ms=latency, error_msg=str(e))
            raise e

    async def chat_stream(self, messages: List[LLMMessage], **kwargs) -> AsyncIterator[str]:
        url = f"{self.host}/api/chat"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": True,
            **kwargs
        }
        
        async def stream_generator():
            start_time = time.time()
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    async with client.stream("POST", url, headers=headers, json=data) as response:
                        response.raise_for_status()
                        import json
                        async for line in response.aiter_lines():
                            if line.strip():
                                try:
                                    j = json.loads(line)
                                    delta = j["message"].get("content", "")
                                    if delta:
                                        yield delta
                                except Exception:
                                    pass
                self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_time) * 1000)
            except Exception as e:
                self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_time) * 1000, error_msg=str(e))
                raise e

        return stream_generator()
