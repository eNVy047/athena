from typing import Protocol, List, Dict, Any, AsyncIterator
from dataclasses import dataclass

@dataclass
class LLMMessage:
    role: str
    content: str

@dataclass
class LLMResponse:
    content: str
    raw_response: Dict[str, Any]

class LLMProvider(Protocol):
    async def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        ...

    async def chat_stream(self, messages: List[LLMMessage], **kwargs) -> AsyncIterator[str]:
        ...

class SpeechProvider(Protocol):
    async def text_to_speech(self, text: str) -> AsyncIterator[bytes]:
        ...

    async def speech_to_text(self, audio_data: bytes) -> str:
        ...
