from dataclasses import dataclass, field
import uuid
from typing import Dict, Any
from friday.voice.speech_context import SpeechContext
from friday.voice.speech_metrics import SpeechMetrics

@dataclass
class VoiceSession:
    """Represents a single continuous voice session."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    context: SpeechContext = field(init=False)
    metrics: SpeechMetrics = field(init=False)
    
    def __post_init__(self):
        self.context = SpeechContext(session_id=self.session_id)
        self.metrics = SpeechMetrics(session_id=self.session_id)
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "metrics": {
                "vad_trigger_time": self.metrics.vad_trigger_time,
                "ttfb_ms": self.metrics.time_to_first_byte_ms
            }
        }
