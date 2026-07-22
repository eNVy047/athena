from abc import abstractmethod
from friday.providers.base.provider import Provider

class SttProvider(Provider):
    @abstractmethod
    async def speech_to_text(self, audio_data: bytes) -> str:
        """Transcribes audio data to text."""
        pass
