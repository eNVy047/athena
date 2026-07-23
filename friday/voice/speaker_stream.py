"""
F.R.I.D.A.Y. Voice — SpeakerStream.

Plays audio bytes through the system speakers.
Handles both raw WAV bytes (from Sarvam) and base64-encoded
audio formats. Uses sounddevice for low-latency playback.
"""
import asyncio
import io
import logging
import wave
from typing import AsyncIterable, Optional

import numpy as np
import sounddevice as sd

logger = logging.getLogger(__name__)


def _decode_wav_bytes(raw: bytes) -> tuple[np.ndarray, int]:
    """
    Decodes WAV-formatted bytes into a numpy int16 array + sample rate.
    WAV files have a 44-byte header followed by raw PCM data.
    """
    try:
        buf = io.BytesIO(raw)
        with wave.open(buf, "rb") as wf:
            sample_rate = wf.getframerate()
            n_frames = wf.getnframes()
            n_channels = wf.getnchannels()
            raw_frames = wf.readframes(n_frames)

        audio = np.frombuffer(raw_frames, dtype=np.int16)
        if n_channels > 1:
            # Downmix to mono
            audio = audio.reshape(-1, n_channels).mean(axis=1).astype(np.int16)
        return audio, sample_rate
    except Exception:
        # Fallback: treat as raw PCM int16 at 22050Hz (Sarvam default)
        audio = np.frombuffer(raw, dtype=np.int16)
        return audio, 22050


def _is_wav(data: bytes) -> bool:
    """Returns True if the bytes start with a WAV RIFF header."""
    return len(data) >= 4 and data[:4] == b"RIFF"


class SpeakerStream:
    """Plays audio data through the system speakers."""

    def __init__(self, sample_rate: int = 22050, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self._is_playing = False

    async def play_stream(
        self, audio_generator: AsyncIterable[bytes], sample_rate: int = 22050
    ) -> None:
        """
        Plays an async stream of audio bytes through the speakers.

        Accepts both:
        - WAV-formatted bytes (from Sarvam, decoded automatically)
        - Raw PCM int16 bytes (from older providers)

        Playback is chunk-by-chunk to minimize latency.
        """
        self._is_playing = True
        logger.info("[SpeakerStream] Playback started at %dHz", sample_rate)
        total_played = 0

        try:
            async for chunk in audio_generator:
                if not self._is_playing:
                    break
                if not chunk:
                    continue

                # Decode WAV header if present, otherwise treat as raw PCM
                if _is_wav(chunk):
                    audio_array, detected_rate = _decode_wav_bytes(chunk)
                    play_rate = detected_rate
                else:
                    audio_array = np.frombuffer(chunk, dtype=np.int16)
                    play_rate = sample_rate

                if len(audio_array) == 0:
                    continue

                # sd.play blocks until the chunk finishes — fine for streaming
                sd.play(audio_array, samplerate=play_rate, blocking=True)
                total_played += len(chunk)

        except Exception as exc:
            logger.error("[SpeakerStream] Playback error: %s", exc)
        finally:
            self._is_playing = False
            logger.info("[SpeakerStream] Playback finished (%d bytes)", total_played)

    async def stop(self) -> None:
        """Stops current playback immediately."""
        self._is_playing = False
        sd.stop()
        logger.info("[SpeakerStream] Playback stopped.")
