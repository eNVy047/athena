import time
import httpx
from typing import List, Dict, Any, AsyncIterator
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.llm.base import LlmProvider, LLMMessage, LLMResponse

class GroqLlmProvider(LlmProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="llm",
            name="groq",
            version="1.0.0",
            capabilities=["chat", "chat_stream"]
        )
        super().__init__(metadata, config)
        self.api_key = config.get("GROQ_API_KEY", "")
        self.model = config.get("LLM_MODEL", "llama-3.3-70b-versatile")
        self.timeout = config.get("PROVIDER_TIMEOUT", 30.0)

    async def initialize(self) -> None:
        if not self.api_key:
            raise ValueError("Groq API Key is required but missing.")

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False

    async def health_check(self) -> bool:
        return bool(self.api_key)

    async def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        start_time = time.time()
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            **kwargs
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                res_json = response.json()
                content = res_json["choices"][0]["message"]["content"]
                
                latency = (time.time() - start_time) * 1000
                self.health_tracker.record_call(
                    success=True,
                    latency_ms=latency,
                    prompt_tokens=res_json.get("usage", {}).get("prompt_tokens", 0),
                    completion_tokens=res_json.get("usage", {}).get("completion_tokens", 0)
                )
                return LLMResponse(content=content, raw_response=res_json)
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.health_tracker.record_call(success=False, latency_ms=latency, error_msg=str(e))
            raise e

    async def chat_stream(self, messages: List[LLMMessage], **kwargs) -> AsyncIterator[str]:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
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
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                content = line[6:]
                                if content.strip() == "[DONE]":
                                    break
                                import json
                                try:
                                    j = json.loads(content)
                                    delta = j["choices"][0]["delta"].get("content", "")
                                    if delta:
                                        yield delta
                                except Exception:
                                    pass
                self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_time) * 1000)
            except Exception as e:
                self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_time) * 1000, error_msg=str(e))
                raise e

        return stream_generator()
