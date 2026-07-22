from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class SpeechResult:
    """Standardized result for a speech-to-text or text-to-speech operation."""
    success: bool
    text: Optional[str] = None
    audio_data: Optional[bytes] = None
    duration_ms: float = 0.0
    confidence: float = 1.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
