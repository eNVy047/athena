from dataclasses import dataclass
from typing import Optional, Dict, Any
from friday.events.event_types import Event

# New Event Types for Voice
VOICE_WAKE_WORD_DETECTED = "voice.wake_word_detected"
VOICE_SPEECH_STARTED = "voice.speech_started"
VOICE_SPEECH_ENDED = "voice.speech_ended"
VOICE_STT_PARTIAL = "voice.stt_partial"
VOICE_STT_FINAL = "voice.stt_final"
VOICE_TTS_STARTED = "voice.tts_started"
VOICE_TTS_ENDED = "voice.tts_ended"
VOICE_INTERRUPTED = "voice.interrupted"
VOICE_SILENCE_TIMEOUT = "voice.silence_timeout"
VOICE_ERROR = "voice.error"

@dataclass
class VoiceEvent(Event):
    """Base event for voice system."""
    session_id: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SpeechDetectedEvent(VoiceEvent):
    """Fired when VAD detects speech (or wake word)."""
    is_wake_word: bool = False

@dataclass
class SttResultEvent(VoiceEvent):
    """Fired when STT returns a result."""
    text: str
    is_final: bool = False
    confidence: float = 0.0

@dataclass
class VoiceInterruptedEvent(VoiceEvent):
    """Fired when user interrupts TTS output."""
    interruption_time_ms: float = 0.0
