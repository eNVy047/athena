from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class SpeechContext:
    """Contextual information for a voice interaction."""
    session_id: str
    user_id: Optional[str] = None
    language: str = "en-US"
    voice_preferences: Dict[str, Any] = field(default_factory=dict)
    
    # Active state trackers
    is_interrupted: bool = False
    current_latency_ms: float = 0.0
    
    # Audio metadata
    sample_rate: int = 16000
    channels: int = 1
