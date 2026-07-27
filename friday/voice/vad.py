import logging
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)

class VoiceActivityDetector:
    """Simple energy-based Voice Activity Detection (VAD)."""
    
    def __init__(self, energy_threshold: float = 200.0, silence_timeout_s: float = 1.5):
        self.energy_threshold = energy_threshold
        self.silence_timeout_s = silence_timeout_s
        self.is_speaking = False
        
        # We would typically use WebRTC VAD or Silero here.
        # For this implementation, we use a simple energy threshold.

    def process_chunk(self, chunk: bytes) -> bool:
        """
        Returns True if speech is detected in the chunk.
        """
        if not chunk:
            return False
            
        audio_array = np.frombuffer(chunk, dtype=np.int16)
        
        # Calculate RMS energy
        if len(audio_array) == 0:
            return False
            
        rms = np.sqrt(np.mean(np.square(audio_array.astype(np.float32))))
        
        detected = rms > self.energy_threshold
        
        if detected != self.is_speaking:
            self.is_speaking = detected
            
        return detected
