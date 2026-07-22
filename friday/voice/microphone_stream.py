import asyncio
import queue
import logging
import sounddevice as sd
from typing import AsyncGenerator, Optional
import numpy as np

logger = logging.getLogger(__name__)

class MicrophoneStream:
    """Captures audio from the microphone and yields PCM chunks."""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1, chunk_size: int = 1024):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self._queue = asyncio.Queue()
        self._stream: Optional[sd.InputStream] = None
        self._is_running = False

    def _audio_callback(self, indata: np.ndarray, frames: int, time, status: sd.CallbackFlags):
        """Called by sounddevice for each audio block."""
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        # Convert numpy array to bytes (PCM 16-bit)
        if self._is_running:
            # We assume indata is float32 or int16 depending on dtype
            # Default sounddevice dtype for float32 is fine, but we'll ask for int16 to send to STT
            self._queue.put_nowait(bytes(indata))

    async def start(self) -> None:
        """Starts the microphone stream."""
        if self._is_running:
            return
            
        self._is_running = True
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='int16',
            blocksize=self.chunk_size,
            callback=self._audio_callback
        )
        self._stream.start()
        logger.info(f"MicrophoneStream started at {self.sample_rate}Hz")

    async def stop(self) -> None:
        """Stops the microphone stream."""
        if not self._is_running:
            return
            
        self._is_running = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
            
        # Put a None sentinel to terminate the generator
        await self._queue.put(None)
        logger.info("MicrophoneStream stopped.")

    async def generate_chunks(self) -> AsyncGenerator[bytes, None]:
        """Yields audio chunks as they are captured."""
        while self._is_running:
            chunk = await self._queue.get()
            if chunk is None:
                break
            yield chunk
