"""
F.R.I.D.A.Y. Voice — MicrophoneStream.

Captures raw PCM int16 audio from the system microphone and yields
it as async chunks. Audio callbacks are thread-safe via asyncio's
call_soon_threadsafe to avoid C-thread/asyncio queue race conditions.
"""
import asyncio
import logging
from typing import AsyncGenerator, Optional

import numpy as np
import sounddevice as sd

logger = logging.getLogger(__name__)


class MicrophoneStream:
    """Captures audio from the microphone and yields PCM int16 chunks."""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self._queue: asyncio.Queue = asyncio.Queue()
        self._stream: Optional[sd.InputStream] = None
        self._is_running = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def _audio_callback(
        self, indata: np.ndarray, frames: int, time, status: sd.CallbackFlags
    ) -> None:
        """
        Called by sounddevice in a C thread for each captured audio block.

        IMPORTANT: We must NOT call asyncio functions directly here.
        Use call_soon_threadsafe to safely schedule the queue put.
        """
        if status:
            logger.warning("[MicrophoneStream] Audio callback status: %s", status)

        if self._is_running and self._loop is not None:
            # Thread-safe: schedule the put on the asyncio event loop
            self._loop.call_soon_threadsafe(
                self._queue.put_nowait, bytes(indata)
            )

    async def start(self) -> None:
        """Starts the microphone stream."""
        if self._is_running:
            return

        self._is_running = True
        # Capture current running event loop for thread-safe callbacks
        self._loop = asyncio.get_running_loop()

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
            blocksize=self.chunk_size,
            callback=self._audio_callback,
        )
        self._stream.start()
        logger.info(
            "[MicrophoneStream] Started at %dHz, %dch, chunk=%d",
            self.sample_rate, self.channels, self.chunk_size,
        )

    async def stop(self) -> None:
        """Stops the microphone stream and drains the queue."""
        if not self._is_running:
            return

        self._is_running = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        # Sentinel to terminate the async generator
        await self._queue.put(None)
        logger.info("[MicrophoneStream] Stopped.")

    async def generate_chunks(self) -> AsyncGenerator[bytes, None]:
        """Yields raw PCM int16 audio chunks as they are captured."""
        while self._is_running:
            chunk = await self._queue.get()
            if chunk is None:
                break
            yield chunk
