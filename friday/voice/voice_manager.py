import logging
from typing import Optional

from friday.voice.speech_pipeline import SpeechPipeline
from friday.agent.agent import Agent
from friday.voice.speech_state import VoiceMode

logger = logging.getLogger(__name__)

class VoiceManager:
    """
    Facade for the Friday Voice Subsystem.
    Initializes and manages the speech pipeline and voice configuration.
    """
    def __init__(self, agent: Agent, stt_provider, tts_provider):
        self.agent = agent
        self.pipeline = SpeechPipeline(agent, stt_provider, tts_provider)
        
    async def start(self, mode: VoiceMode = VoiceMode.CONTINUOUS):
        """Starts the voice system."""
        logger.info(f"Starting Voice System in {mode.name} mode.")
        self.pipeline.conversation_manager.mode = mode
        await self.pipeline.start()
        
    async def stop(self):
        """Stops the voice system."""
        logger.info("Stopping Voice System.")
        await self.pipeline.stop()
        
    async def start_recording(self):
        """Used in Push-To-Talk to begin buffering."""
        if not self.pipeline._is_running:
            self.pipeline.conversation_manager.mode = VoiceMode.PUSH_TO_TALK
            await self.pipeline.start()
        self.pipeline.start_ptt_recording()

    async def stop_recording(self):
        """Used in Push-To-Talk to end buffering and trigger processing."""
        self.pipeline.stop_ptt_recording()
        
    def set_wake_word(self, wake_words: list[str]):
        """Configures the active wake words."""
        self.pipeline.wake_word.wake_words = [w.lower() for w in wake_words]
        
    def enable_noise_reduction(self, enable: bool = True):
        self.pipeline.audio_router.enable_noise_reduction(enable)
        
    def enable_echo_cancellation(self, enable: bool = True):
        self.pipeline.audio_router.enable_echo_cancellation(enable)
