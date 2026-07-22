from abc import abstractmethod
from typing import List, Dict, Any, AsyncIterator
from dataclasses import dataclass
from friday.providers.base.provider import Provider

@dataclass
class LLMMessage:
    role: str
    content: str

@dataclass
class LLMResponse:
    content: str
    raw_response: Dict[str, Any]

class LlmProvider(Provider):
    @abstractmethod
    async def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Sends a list of messages to the model and returns response."""
        pass

    @abstractmethod
    async def chat_stream(self, messages: List[LLMMessage], **kwargs) -> AsyncIterator[str]:
        """Streams response tokens from the model."""
        pass
