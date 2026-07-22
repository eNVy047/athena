import asyncio
import logging
import sounddevice as sd
from typing import AsyncIterable, Optional

logger = logging.getLogger(__name__)

class SpeakerStream:
    """Plays PCM audio data through the system speakers."""
    
    def __init__(self, sample_rate: int = 24000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self._stream: Optional[sd.OutputStream] = None
        self._is_playing = False
        self._queue = asyncio.Queue(maxsize=100) # Buffer to prevent memory runaway

    def _audio_callback(self, outdata, frames, time, status):
        """Called by sounddevice when it needs more audio data."""
        if status:
            logger.warning(f"Speaker callback status: {status}")
            
        try:
            # We must provide exactly 'frames' of data
            # For simplicity, we just use raw sd.play instead of a complex queueing callback for now,
            # or we do a non-blocking pull from a thread-safe queue.
            pass
        except queue.Empty:
            outdata.fill(0)

    async def play_stream(self, audio_generator: AsyncIterable[bytes], sample_rate: int = 24000) -> None:
        """Plays an async stream of audio bytes."""
        import numpy as np
        
        self._is_playing = True
        logger.info(f"Started SpeakerStream playback at {sample_rate}Hz")
        
        # Simple blocking playback wrapped in async for MVP
        # In a production system, use OutputStream with a callback queue.
        # But since providers often return chunks, we accumulate or play them sequentially.
        try:
            async for chunk in audio_generator:
                if not self._is_playing:
                    break
                    
                if chunk:
                    # Convert bytes to int16 numpy array
                    audio_array = np.frombuffer(chunk, dtype=np.int16)
                    # Use blocking play for the chunk. To make truly async, use OutputStream.
                    sd.play(audio_array, samplerate=sample_rate, blocking=True)
                    
        except Exception as e:
            logger.error(f"Error in SpeakerStream: {e}")
        finally:
            self._is_playing = False
            logger.info("SpeakerStream playback finished.")

    async def stop(self) -> None:
        """Stops current playback."""
        self._is_playing = False
        sd.stop()
        logger.info("SpeakerStream stopped.")
