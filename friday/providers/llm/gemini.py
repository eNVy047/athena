import time
import httpx
from typing import List, Dict, Any, AsyncIterator
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.llm.base import LlmProvider, LLMMessage, LLMResponse

class GeminiLlmProvider(LlmProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="llm",
            name="gemini",
            version="1.0.0",
            capabilities=["chat", "chat_stream"]
        )
        super().__init__(metadata, config)
        self.api_key = config.get("GEMINI_API_KEY", "")
        self.model = config.get("LLM_MODEL", "gemini-2.5-flash")
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

    async def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        start_time = time.time()
        # Using Gemini Developer API (v1beta or v1)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        
        # Format messages for Gemini API
        contents = []
        for m in messages:
            role = "user" if m.role == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m.content}]})

        data = {"contents": contents}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                res_json = response.json()
                content = res_json["candidates"][0]["content"]["parts"][0]["text"]
                
                latency = (time.time() - start_time) * 1000
                self.health_tracker.record_call(success=True, latency_ms=latency)
                return LLMResponse(content=content, raw_response=res_json)
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.health_tracker.record_call(success=False, latency_ms=latency, error_msg=str(e))
            raise e

    async def chat_stream(self, messages: List[LLMMessage], **kwargs) -> AsyncIterator[str]:
        # Stream implementation for Gemini
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:streamGenerateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        
        contents = []
        for m in messages:
            role = "user" if m.role == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m.content}]})

        data = {"contents": contents}

        async def stream_generator():
            start_time = time.time()
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    async with client.stream("POST", url, headers=headers, json=data) as response:
                        response.raise_for_status()
                        import json
                        async for line in response.aiter_lines():
                            if line.strip().startswith('"text":'):
                                # Quick text extraction fallback
                                pass
                            # Full JSON stream handling
                            # Gemini stream is returned as a JSON array of parts, or chunks
                            # For simple robust integration, parse the chunk or yield text
                            if line.startswith("data: ") or line.strip().startswith("{"):
                                # Yield chunk content if JSON parsed
                                try:
                                    j = json.loads(line.strip().strip(",").strip("[").strip("]"))
                                    text = j["candidates"][0]["content"]["parts"][0]["text"]
                                    if text:
                                        yield text
                                except Exception:
                                    pass
                self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_time) * 1000)
            except Exception as e:
                self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_time) * 1000, error_msg=str(e))
                raise e

        return stream_generator()
