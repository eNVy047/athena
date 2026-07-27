"""
Sarvam AI Provider — Speech-to-Text (STT) implementation.

Supports WAV/PCM audio input with automatic retry and graceful
fallback signaling to the ProviderManager.
"""
import io
import logging
import time
import wave
from typing import Any, Dict

from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.stt.base import SttProvider
from friday.providers.sarvam.sarvam_client import SarvamClient
from friday.providers.sarvam.sarvam_config import SarvamConfig
from friday.providers.sarvam.sarvam_exceptions import SarvamAuthError, SarvamError

logger = logging.getLogger(__name__)


class SarvamSttProvider(SttProvider):
    """
    Sarvam AI Speech-to-Text provider.

    Converts raw PCM/WAV audio bytes to transcribed text using
    the Sarvam saarika ASR model. Supports Indian languages including
    Hindi (hi-IN), Tamil (ta-IN), Telugu (te-IN), and English (en-IN).
    """

    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="stt",
            name="sarvam",
            version="1.0.0",
            capabilities=["speech_to_text", "multilingual"],
        )
        super().__init__(metadata, config)
        self._sarvam_config = SarvamConfig.from_env()
        self._client: SarvamClient | None = None

    async def initialize(self) -> None:
        if not self._sarvam_config.api_key:
            raise SarvamAuthError(
                "SARVAM_API_KEY is not set. Sarvam STT will not be available."
            )
        self._client = SarvamClient(self._sarvam_config)
        logger.info("[SarvamSTT] Provider initialized (model=%s)", self._sarvam_config.stt_model)

    async def connect(self) -> None:
        self.is_connected = True
        logger.info("[SarvamSTT] Connected.")

    async def disconnect(self) -> None:
        self.is_connected = False
        self._client = None
        logger.info("[SarvamSTT] Disconnected.")

    async def health_check(self) -> bool:
        return bool(self._sarvam_config.api_key) and self.is_connected

    def _pcm_to_wav_bytes(self, pcm_data: bytes, sample_rate: int = 16000, channels: int = 1) -> bytes:
        """
        Wraps raw PCM int16 audio in a proper WAV container for Sarvam API.
        Sarvam STT expects WAV format.
        """
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)  # 16-bit PCM = 2 bytes
            wf.setframerate(sample_rate)
            wf.writeframes(pcm_data)
        return buf.getvalue()

    async def speech_to_text(self, audio_data: bytes) -> str:
        """
        Transcribes audio bytes to text using Sarvam saarika ASR model.

        Accepts raw PCM bytes (int16, 16kHz, mono) and wraps them in
        a WAV container before sending to the Sarvam API.
        """
        if not self._client:
            raise SarvamAuthError("SarvamSttProvider not initialized. Call initialize() first.")

        start_time = time.time()

        try:
            # Wrap raw PCM in WAV for Sarvam API
            wav_data = self._pcm_to_wav_bytes(audio_data)

            files = {
                "file": ("audio.wav", wav_data, "audio/wav"),
            }
            data = {
                "model": self._sarvam_config.stt_model,
                "language_code": self._sarvam_config.language,
                "with_timestamps": "false",
                "with_disfluencies": "false",
            }

            response = await self._client.post_multipart(
                endpoint=SarvamConfig.STT_ENDPOINT,
                files=files,
                data=data,
            )

            transcript = response.get("transcript", "")
            latency_ms = (time.time() - start_time) * 1000
            self.health_tracker.record_call(success=True, latency_ms=latency_ms)
            logger.info(
                "[SarvamSTT] Transcribed %d chars in %.0fms", len(transcript), latency_ms
            )
            return transcript

        except SarvamError as exc:
            latency_ms = (time.time() - start_time) * 1000
            self.health_tracker.record_call(
                success=False, latency_ms=latency_ms, error_msg=str(exc)
            )
            logger.error("[SarvamSTT] Transcription failed: %s", exc)
            raise
        except Exception as exc:
            latency_ms = (time.time() - start_time) * 1000
            self.health_tracker.record_call(
                success=False, latency_ms=latency_ms, error_msg=str(exc)
            )
            logger.error("[SarvamSTT] Unexpected error during transcription: %s", exc)
            raise
