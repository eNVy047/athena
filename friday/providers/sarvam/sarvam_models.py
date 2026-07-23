"""
Sarvam AI Provider — Pydantic models for request/response payloads.
"""
from typing import Optional, List
from pydantic import BaseModel


# ── STT Models ─────────────────────────────────────────────────────────────

class SarvamSTTRequest(BaseModel):
    """Payload for Sarvam /speech-to-text endpoint."""
    model: str = "saarika:v2"
    language_code: str = "hi-IN"
    with_timestamps: bool = False
    with_disfluencies: bool = False


class SarvamSTTWord(BaseModel):
    word: str
    start: Optional[float] = None
    end: Optional[float] = None


class SarvamSTTResult(BaseModel):
    transcript: str
    language_code: Optional[str] = None
    words: Optional[List[SarvamSTTWord]] = None


class SarvamSTTResponse(BaseModel):
    """Response from Sarvam /speech-to-text endpoint."""
    transcript: str
    language_code: Optional[str] = None
    request_id: Optional[str] = None


# ── TTS Models ─────────────────────────────────────────────────────────────

class SarvamTTSRequest(BaseModel):
    """Payload for Sarvam /text-to-speech endpoint."""
    inputs: List[str]
    target_language_code: str = "hi-IN"
    speaker: str = "meera"
    pitch: float = 0.0
    pace: float = 1.0
    loudness: float = 1.0
    speech_sample_rate: int = 22050
    enable_preprocessing: bool = True
    model: str = "bulbul:v1"


class SarvamTTSAudio(BaseModel):
    """Single audio chunk from TTS response."""
    audios: List[str]  # base64-encoded MP3 chunks


class SarvamTTSResponse(BaseModel):
    """Response from Sarvam /text-to-speech endpoint."""
    audios: List[str]  # list of base64-encoded WAV/MP3 strings
    request_id: Optional[str] = None
