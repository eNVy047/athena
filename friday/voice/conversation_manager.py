import logging
from typing import Optional
from friday.voice.speech_state import SpeechState, VoiceMode

logger = logging.getLogger(__name__)

class VoiceConversationManager:
    """
    Manages the real-time turn-taking logic, interruption state, 
    and push-to-talk vs continuous listening modes for voice.
    """
    
    def __init__(self, mode: VoiceMode = VoiceMode.CONTINUOUS):
        self.mode = mode
        self.state = SpeechState.IDLE
        self.is_interrupted = False
        self.silence_timeout_s = 2.0
        
    def set_state(self, new_state: SpeechState):
        """Transitions to a new state and handles logic if interrupted."""
        if self.state == new_state:
            return
            
        logger.info(f"Voice state transition: {self.state.name} -> {new_state.name}")
        self.state = new_state
        
        if new_state == SpeechState.LISTENING:
            self.is_interrupted = False
            
    def handle_interruption(self):
        """Called when user starts speaking while TTS is playing."""
        if self.state == SpeechState.SPEAKING:
            logger.info("User interrupted the agent.")
            self.is_interrupted = True
            self.set_state(SpeechState.INTERRUPTED)
            
    def should_process_audio(self) -> bool:
        """Determines if incoming audio should be processed by STT based on current mode/state."""
        if self.mode == VoiceMode.PUSH_TO_TALK:
            return self.state == SpeechState.LISTENING
            
        # Continuous mode: we process if we are actively listening (wake word triggered)
        return self.state == SpeechState.LISTENING
