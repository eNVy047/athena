"""
Sarvam AI Provider — Text-to-Speech (TTS) implementation.

Returns async generator of raw PCM bytes decoded from the base64-encoded
WAV audio returned by the Sarvam bulbul TTS model.
"""
import asyncio
import base64
import io
import logging
import time
from typing import Any, AsyncIterator, Dict

from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.tts.base import TtsProvider
from friday.providers.sarvam.sarvam_client import SarvamClient
from friday.providers.sarvam.sarvam_config import SarvamConfig
from friday.providers.sarvam.sarvam_exceptions import SarvamAuthError, SarvamError

logger = logging.getLogger(__name__)


class SarvamTtsProvider(TtsProvider):
    """
    Sarvam AI Text-to-Speech provider.

    Synthesizes text to speech using Sarvam's bulbul TTS model,
    returning raw PCM audio bytes suitable for SpeakerStream playback.
    Supports Indian languages: hi-IN, en-IN, ta-IN, te-IN, etc.
    """

    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="tts",
            name="sarvam",
            version="1.0.0",
            capabilities=["text_to_speech", "multilingual"],
        )
        super().__init__(metadata, config)
        self._sarvam_config = SarvamConfig.from_env()
        self._client: SarvamClient | None = None

    async def initialize(self) -> None:
        if not self._sarvam_config.api_key:
            raise SarvamAuthError(
                "SARVAM_API_KEY is not set. Sarvam TTS will not be available."
            )
        self._client = SarvamClient(self._sarvam_config)
        logger.info("[SarvamTTS] Provider initialized (model=%s, speaker=%s)",
                    self._sarvam_config.tts_model, self._sarvam_config.tts_speaker)

    async def connect(self) -> None:
        self.is_connected = True
        logger.info("[SarvamTTS] Connected.")

    async def disconnect(self) -> None:
        self.is_connected = False
        self._client = None
        logger.info("[SarvamTTS] Disconnected.")

    async def health_check(self) -> bool:
        return bool(self._sarvam_config.api_key) and self.is_connected

    def _chunk_text(self, text: str, max_chars: int = 500) -> list[str]:
        """
        Splits long text into chunks ≤ max_chars for Sarvam's API limit.
        Splits on sentence boundaries where possible.
        """
        if len(text) <= max_chars:
            return [text]

        chunks = []
        sentences = text.replace(". ", ".|").replace("! ", "!|").replace("? ", "?|").split("|")
        current = ""
        for sentence in sentences:
            if len(current) + len(sentence) + 1 <= max_chars:
                current = (current + " " + sentence).strip()
            else:
                if current:
                    chunks.append(current)
                current = sentence
        if current:
            chunks.append(current)
        return chunks or [text[:max_chars]]

    async def text_to_speech(self, text: str) -> AsyncIterator[bytes]:
        """
        Synthesizes text to audio using Sarvam bulbul TTS model.

        Yields raw PCM int16 bytes suitable for sounddevice playback.
        Long texts are chunked automatically to stay within API limits.
        """
        if not self._client:
            raise SarvamAuthError("SarvamTtsProvider not initialized. Call initialize() first.")

        async def stream_generator() -> AsyncIterator[bytes]:
            start_time = time.time()
            chunks = self._chunk_text(text)
            total_bytes = 0

            try:
                for chunk_text in chunks:
                    payload = {
                        "inputs": [chunk_text],
                        "target_language_code": self._sarvam_config.language,
                        "speaker": self._sarvam_config.tts_speaker,
                        "pitch": 0.0,
                        "pace": 1.0,
                        "loudness": 1.5,
                        "speech_sample_rate": 22050,
                        "enable_preprocessing": True,
                        "model": self._sarvam_config.tts_model,
                    }

                    response = await self._client.post_json(
                        endpoint=SarvamConfig.TTS_ENDPOINT,
                        payload=payload,
                    )

                    audios = response.get("audios", [])
                    for b64_audio in audios:
                        if not b64_audio:
                            continue
                        # Sarvam returns base64-encoded WAV bytes
                        raw_bytes = base64.b64decode(b64_audio)
                        total_bytes += len(raw_bytes)
                        yield raw_bytes

                latency_ms = (time.time() - start_time) * 1000
                self.health_tracker.record_call(success=True, latency_ms=latency_ms)
                logger.info(
                    "[SarvamTTS] Synthesized %d bytes in %.0fms (%d chunks)",
                    total_bytes, latency_ms, len(chunks),
                )

            except SarvamError as exc:
                latency_ms = (time.time() - start_time) * 1000
                self.health_tracker.record_call(
                    success=False, latency_ms=latency_ms, error_msg=str(exc)
                )
                logger.error("[SarvamTTS] Synthesis failed: %s", exc)
                raise
            except Exception as exc:
                latency_ms = (time.time() - start_time) * 1000
                self.health_tracker.record_call(
                    success=False, latency_ms=latency_ms, error_msg=str(exc)
                )
                logger.error("[SarvamTTS] Unexpected error: %s", exc)
                raise

        return stream_generator()
