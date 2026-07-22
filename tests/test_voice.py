import pytest
from typing import AsyncIterator
from friday.domain.provider import SpeechProvider

class MockSpeechProvider:
    async def text_to_speech(self, text: str) -> AsyncIterator[bytes]:
        async def mock_generator():
            yield b"audio_chunk"
        return mock_generator()

    async def speech_to_text(self, audio_data: bytes) -> str:
        return "Friday open Chrome"

@pytest.mark.asyncio
async def test_speech_pipeline():
    provider = MockSpeechProvider()
    
    # 1. Test STT conversion
    stt_res = await provider.speech_to_text(b"audio_bytes")
    assert stt_res == "Friday open Chrome"
    
    # 2. Test TTS stream
    generator = await provider.text_to_speech("System online.")
    chunks = [chunk async for chunk in generator]
    assert len(chunks) == 1
    assert chunks[0] == b"audio_chunk"
