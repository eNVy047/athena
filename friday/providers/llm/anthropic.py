import time
import httpx
from typing import List, Dict, Any, AsyncIterator
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.llm.base import LlmProvider, LLMMessage, LLMResponse

class AnthropicLlmProvider(LlmProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="llm",
            name="anthropic",
            version="1.0.0",
            capabilities=["chat", "chat_stream"]
        )
        super().__init__(metadata, config)
        self.api_key = config.get("ANTHROPIC_API_KEY", "")
        self.model = config.get("LLM_MODEL", "claude-3-5-sonnet-20240620")
        self.timeout = config.get("PROVIDER_TIMEOUT", 30.0)

    async def initialize(self) -> None:
        if not self.api_key:
            raise ValueError("Anthropic API Key is required but missing.")

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False

    async def health_check(self) -> bool:
        return bool(self.api_key)

    async def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        start_time = time.time()
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        # Pull system prompt from system role if any, or map roles
        system_prompt = ""
        user_messages = []
        for m in messages:
            if m.role == "system":
                system_prompt = m.content
            else:
                user_messages.append({"role": m.role, "content": m.content})
                
        data = {
            "model": self.model,
            "messages": user_messages,
            "max_tokens": 4096,
            **kwargs
        }
        if system_prompt:
            data["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                res_json = response.json()
                content = res_json["content"][0]["text"]
                
                latency = (time.time() - start_time) * 1000
                self.health_tracker.record_call(
                    success=True,
                    latency_ms=latency,
                    prompt_tokens=res_json.get("usage", {}).get("input_tokens", 0),
                    completion_tokens=res_json.get("usage", {}).get("output_tokens", 0)
                )
                return LLMResponse(content=content, raw_response=res_json)
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.health_tracker.record_call(success=False, latency_ms=latency, error_msg=str(e))
            raise e

    async def chat_stream(self, messages: List[LLMMessage], **kwargs) -> AsyncIterator[str]:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        system_prompt = ""
        user_messages = []
        for m in messages:
            if m.role == "system":
                system_prompt = m.content
            else:
                user_messages.append({"role": m.role, "content": m.content})
                
        data = {
            "model": self.model,
            "messages": user_messages,
            "max_tokens": 4096,
            "stream": True,
            **kwargs
        }
        if system_prompt:
            data["system"] = system_prompt

        async def stream_generator():
            start_time = time.time()
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    async with client.stream("POST", url, headers=headers, json=data) as response:
                        response.raise_for_status()
                        import json
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                content = line[6:]
                                try:
                                    j = json.loads(content)
                                    if j.get("type") == "content_block_delta":
                                        delta = j["delta"].get("text", "")
                                        if delta:
                                            yield delta
                                except Exception:
                                    pass
                self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_time) * 1000)
            except Exception as e:
                self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_time) * 1000, error_msg=str(e))
                raise e

        return stream_generator()
