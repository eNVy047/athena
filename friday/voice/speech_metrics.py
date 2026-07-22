from dataclasses import dataclass
import time

@dataclass
class SpeechMetrics:
    """Tracks latency and performance of the voice pipeline."""
    session_id: str
    
    # Timestamps
    interaction_start_time: float = 0.0
    vad_trigger_time: float = 0.0
    stt_start_time: float = 0.0
    stt_end_time: float = 0.0
    agent_start_time: float = 0.0
    agent_end_time: float = 0.0
    tts_start_time: float = 0.0
    tts_first_byte_time: float = 0.0
    interaction_end_time: float = 0.0
    
    def start_interaction(self):
        self.interaction_start_time = time.time()
        
    def record_vad(self):
        self.vad_trigger_time = time.time()
        
    def record_stt_start(self):
        self.stt_start_time = time.time()
        
    def record_stt_end(self):
        self.stt_end_time = time.time()
        
    def record_agent_start(self):
        self.agent_start_time = time.time()
        
    def record_agent_end(self):
        self.agent_end_time = time.time()
        
    def record_tts_start(self):
        self.tts_start_time = time.time()
        
    def record_tts_first_byte(self):
        self.tts_first_byte_time = time.time()
        
    def end_interaction(self):
        self.interaction_end_time = time.time()

    @property
    def time_to_first_byte_ms(self) -> float:
        """Total time from user stopping speech to hearing first audio byte."""
        if self.tts_first_byte_time and self.vad_trigger_time:
            return (self.tts_first_byte_time - self.vad_trigger_time) * 1000
        return 0.0
