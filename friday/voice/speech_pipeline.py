"""
F.R.I.D.A.Y. Voice — SpeechPipeline.

Coordinates real-time audio: Microphone → VAD → Wake Word → STT → Agent → TTS → Speaker.
"""
import asyncio
import logging
from typing import Optional

from friday.voice.microphone_stream import MicrophoneStream
from friday.voice.speaker_stream import SpeakerStream
from friday.voice.vad import VoiceActivityDetector
from friday.voice.wake_word import WakeWordDetector
from friday.voice.audio_router import AudioRouter
from friday.voice.conversation_manager import VoiceConversationManager
from friday.voice.speech_state import SpeechState, VoiceMode

logger = logging.getLogger(__name__)


class SpeechPipeline:
    """
    Coordinates the real-time audio flow:
    Microphone → VAD → Wake Word → STT → Agent → TTS → Speaker
    """

    def __init__(self, agent, stt_provider, tts_provider, response_callback=None):
        """
        Args:
            agent: FridayAgent instance (has process_input(query) coroutine)
            stt_provider: Active STT provider (has speech_to_text(bytes) coroutine)
            tts_provider: Active TTS provider (has text_to_speech(str) → async iterator)
            response_callback: Optional async callable(text) to emit voice responses to UI
        """
        self.agent = agent
        self.stt = stt_provider
        self.tts = tts_provider
        self.response_callback = response_callback

        self.microphone = MicrophoneStream()
        self.speaker = SpeakerStream()
        self.vad = VoiceActivityDetector()
        self.wake_word = WakeWordDetector()
        self.audio_router = AudioRouter()
        self.conversation_manager = VoiceConversationManager(mode=VoiceMode.CONTINUOUS)

        self._is_running = False

    async def start(self) -> None:
        """Starts the background microphone listening loop."""
        if self._is_running:
            return
        self._is_running = True
        await self.microphone.start()
        asyncio.create_task(self._process_microphone_stream())
        logger.info("[SpeechPipeline] Started in %s mode.", self.conversation_manager.mode.name)

    async def stop(self) -> None:
        """Stops the pipeline and releases audio resources."""
        self._is_running = False
        await self.microphone.stop()
        await self.speaker.stop()
        logger.info("[SpeechPipeline] Stopped.")

    async def _process_microphone_stream(self) -> None:
        """Main audio processing loop."""
        buffer = bytearray()

        async for chunk in self.microphone.generate_chunks():
            if not self._is_running:
                break

            # Interruption: if we are speaking and user starts talking, interrupt
            if self.conversation_manager.state == SpeechState.SPEAKING:
                if self.vad.process_chunk(chunk):
                    logger.info("[SpeechPipeline] Interruption detected.")
                    self.conversation_manager.handle_interruption()
                    await self.speaker.stop()

            processed_chunk = self.audio_router.process_input(
                chunk, self.microphone.sample_rate, self.microphone.channels
            )

            # CONTINUOUS mode: check for wake word before entering LISTENING
            if (
                self.conversation_manager.mode == VoiceMode.CONTINUOUS
                and self.conversation_manager.state == SpeechState.IDLE
            ):
                if self.vad.process_chunk(processed_chunk):
                    buffer.extend(processed_chunk)
                elif len(buffer) > 0:
                    audio_data = bytes(buffer)
                    buffer.clear()
                    try:
                        text = await self.stt.speech_to_text(audio_data)
                        if text and self.wake_word.detect(text):
                            logger.info("[SpeechPipeline] Wake word detected. Listening...")
                            self.conversation_manager.set_state(SpeechState.LISTENING)
                    except Exception as exc:
                        logger.error("[SpeechPipeline] STT error during wake word check: %s", exc)

            # LISTENING: buffer speech until silence, then process
            elif self.conversation_manager.state == SpeechState.LISTENING:
                if self.vad.process_chunk(processed_chunk):
                    buffer.extend(processed_chunk)
                elif len(buffer) > 0:
                    self.conversation_manager.set_state(SpeechState.PROCESSING)
                    audio_data = bytes(buffer)
                    buffer.clear()
                    asyncio.create_task(self._handle_command(audio_data))

    async def _handle_command(self, audio_data: bytes) -> None:
        """STT → Agent → TTS pipeline for a single voice command."""
        try:
            # 1. Speech-to-Text
            text = await self.stt.speech_to_text(audio_data)
            logger.info("[SpeechPipeline] STT transcript: %r", text)

            if not text or not text.strip():
                self.conversation_manager.set_state(SpeechState.IDLE)
                return

            # 2. Agent Execution — use process_input() which is the correct method on FridayAgent
            response = await self.agent.process_input(text)

            # 3. Emit text response to UI if callback is registered
            if self.response_callback and response:
                await self.response_callback(text, response)

            # 4. Text-to-Speech → Speaker
            if response:
                self.conversation_manager.set_state(SpeechState.SPEAKING)
                logger.info("[SpeechPipeline] TTS: %r", response[:80])
                tts_stream = await self.tts.text_to_speech(response)
                await self.speaker.play_stream(tts_stream, sample_rate=22050)

        except Exception as exc:
            logger.error("[SpeechPipeline] Command handling error: %s", exc, exc_info=True)
            self.conversation_manager.set_state(SpeechState.ERROR)
        finally:
            if not self.conversation_manager.is_interrupted:
                self.conversation_manager.set_state(SpeechState.IDLE)
