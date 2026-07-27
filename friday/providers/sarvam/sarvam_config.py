"""
Sarvam AI Provider — Configuration constants and endpoint definitions.
"""
import os


class SarvamConfig:
    """Reads Sarvam configuration from environment variables."""

    # Base API endpoint (Sarvam public API v1)
    BASE_URL: str = "https://api.sarvam.ai"

    # Speech-to-Text endpoint
    STT_ENDPOINT: str = "/speech-to-text"

    # Text-to-Speech endpoint
    TTS_ENDPOINT: str = "/text-to-speech"

    # Translate endpoint (reserved for future use)
    TRANSLATE_ENDPOINT: str = "/translate"

    # Default STT model (saarika = Sarvam's Hindi/English bilingual ASR)
    DEFAULT_STT_MODEL: str = "saarika:v2.5"

    # Default TTS model (bulbul = Sarvam's multilingual TTS voice model)
    DEFAULT_TTS_MODEL: str = "bulbul:v3"

    # Default language for STT and TTS (BCP-47 tags: hi-IN, en-IN, ta-IN, te-IN, etc.)
    DEFAULT_LANGUAGE: str = "en-IN"

    # Default speaker for TTS
    DEFAULT_TTS_SPEAKER: str = "ritu"

    # Default HTTP timeout in seconds
    DEFAULT_TIMEOUT: float = 30.0

    @classmethod
    def from_env(cls) -> "SarvamConfig":
        """Returns a SarvamConfig instance populated from environment variables."""
        instance = cls()
        instance.api_key: str = os.getenv("SARVAM_API_KEY", "")
        instance.stt_model: str = os.getenv("SARVAM_STT_MODEL", cls.DEFAULT_STT_MODEL)
        instance.tts_model: str = os.getenv("SARVAM_TTS_MODEL", cls.DEFAULT_TTS_MODEL)
        instance.language: str = os.getenv("SARVAM_LANGUAGE", cls.DEFAULT_LANGUAGE)
        instance.tts_speaker: str = os.getenv("SARVAM_TTS_SPEAKER", cls.DEFAULT_TTS_SPEAKER)
        instance.timeout: float = float(os.getenv("PROVIDER_TIMEOUT", str(cls.DEFAULT_TIMEOUT)))
        return instance
