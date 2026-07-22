import asyncio
import logging
from typing import Optional, AsyncGenerator

from friday.voice.microphone_stream import MicrophoneStream
from friday.voice.speaker_stream import SpeakerStream
from friday.voice.vad import VoiceActivityDetector
from friday.voice.wake_word import WakeWordDetector
from friday.voice.audio_router import AudioRouter
from friday.voice.conversation_manager import VoiceConversationManager
from friday.voice.speech_state import SpeechState, VoiceMode
from friday.agent.agent import Agent

logger = logging.getLogger(__name__)

class SpeechPipeline:
    """
    Coordinates the real-time audio flow: 
    Microphone -> VAD -> Wake Word -> STT -> Agent -> TTS -> Speaker
    """
    
    def __init__(self, agent: Agent, stt_provider, tts_provider):
        self.agent = agent
        self.stt = stt_provider
        self.tts = tts_provider
        
        self.microphone = MicrophoneStream()
        self.speaker = SpeakerStream()
        self.vad = VoiceActivityDetector()
        self.wake_word = WakeWordDetector()
        self.audio_router = AudioRouter()
        self.conversation_manager = VoiceConversationManager(mode=VoiceMode.CONTINUOUS)
        
        self._is_running = False

    async def start(self):
        """Starts the background listening loop."""
        if self._is_running:
            return
            
        self._is_running = True
        await self.microphone.start()
        asyncio.create_task(self._process_microphone_stream())
        logger.info("SpeechPipeline started.")

    async def stop(self):
        """Stops the pipeline."""
        self._is_running = False
        await self.microphone.stop()
        await self.speaker.stop()
        logger.info("SpeechPipeline stopped.")

    async def _process_microphone_stream(self):
        """Main audio processing loop."""
        buffer = bytearray()
        
        async for chunk in self.microphone.generate_chunks():
            if not self._is_running:
                break
                
            # Interruption handling
            if self.conversation_manager.state == SpeechState.SPEAKING:
                if self.vad.process_chunk(chunk):
                    # User interrupted
                    self.conversation_manager.handle_interruption()
                    await self.speaker.stop()
                    
            processed_chunk = self.audio_router.process_input(
                chunk, 
                self.microphone.sample_rate, 
                self.microphone.channels
            )
            
            # Continuous mode: Check Wake Word
            if self.conversation_manager.mode == VoiceMode.CONTINUOUS and self.conversation_manager.state == SpeechState.IDLE:
                # In a real streaming STT, we'd send audio directly and check text.
                # Here we buffer until VAD says speech ended, then check wake word + text.
                if self.vad.process_chunk(processed_chunk):
                    buffer.extend(processed_chunk)
                elif len(buffer) > 0:
                    # Speech ended, process buffer
                    audio_data = bytes(buffer)
                    buffer.clear()
                    
                    try:
                        text = await self.stt.speech_to_text(audio_data)
                        if self.wake_word.detect(text):
                            logger.info("Wake word triggered! Listening for command...")
                            self.conversation_manager.set_state(SpeechState.LISTENING)
                    except Exception as e:
                        logger.error(f"STT error during wake word check: {e}")
            
            # Active Listening mode
            elif self.conversation_manager.state == SpeechState.LISTENING:
                if self.vad.process_chunk(processed_chunk):
                    buffer.extend(processed_chunk)
                elif len(buffer) > 0:
                    # Silence detected, process command
                    self.conversation_manager.set_state(SpeechState.PROCESSING)
                    audio_data = bytes(buffer)
                    buffer.clear()
                    
                    asyncio.create_task(self._handle_command(audio_data))

    async def _handle_command(self, audio_data: bytes):
        """Sends audio to STT, then Agent, then TTS."""
        try:
            # 1. STT
            text = await self.stt.speech_to_text(audio_data)
            logger.info(f"User (Voice): {text}")
            
            if not text.strip():
                self.conversation_manager.set_state(SpeechState.IDLE)
                return

            # 2. Agent
            agent_result = await self.agent.process_request(
                text, 
                session_id="voice-session"
            )
            
            # 3. TTS
            if agent_result.response:
                self.conversation_manager.set_state(SpeechState.SPEAKING)
                logger.info(f"Agent (Voice): {agent_result.response}")
                
                tts_stream = self.tts.text_to_speech(agent_result.response)
                
                # 4. Speaker Output
                await self.speaker.play_stream(tts_stream)
                
        except Exception as e:
            logger.error(f"Error handling voice command: {e}")
            self.conversation_manager.set_state(SpeechState.ERROR)
            
        finally:
            if not self.conversation_manager.is_interrupted:
                self.conversation_manager.set_state(SpeechState.IDLE)
