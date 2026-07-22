from abc import abstractmethod
from typing import AsyncIterator
from friday.providers.base.provider import Provider

class TtsProvider(Provider):
    @abstractmethod
    async def text_to_speech(self, text: str) -> AsyncIterator[bytes]:
        """Synthesizes text into audio bytes stream."""
        pass
