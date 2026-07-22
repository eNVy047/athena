import logging
import numpy as np
import sounddevice as sd
from typing import Dict, Any
from friday.perception.sensor import Sensor
from friday.perception.sensor_metadata import SensorMetadata, SensorStatus
from friday.perception.sensor_context import SensorContext
from friday.perception.sensor_result import SensorResult

logger = logging.getLogger(__name__)

class MicrophoneSensor(Sensor):
    def __init__(self):
        metadata = SensorMetadata(
            name="microphone",
            description="Observes audio input from microphone using sounddevice",
            version="1.0.0",
            capabilities=["audio.speech_detection"],
            required_permissions=[]
        )
        super().__init__(metadata)
        self.sample_rate = 16000
        self.channels = 1
        self.device = "default"

    async def initialize(self, context: SensorContext) -> None:
        await super().initialize(context)
        self.device = self.context.config.get("MIC_DEVICE", "default")

    async def start(self) -> None:
        await super().start()

    async def pause(self) -> None:
        await super().pause()

    async def resume(self) -> None:
        await super().resume()

    async def stop(self) -> None:
        await super().stop()

    async def health_check(self) -> bool:
        try:
            # Query standard audio device list
            devices = sd.query_devices()
            return len(devices) > 0
        except Exception:
            return False

    async def observe(self) -> SensorResult:
        if self.status != SensorStatus.RUNNING:
            return SensorResult(success=False, error="Sensor not running")

        try:
            # Record a short 0.5-second snippet to process
            duration = 0.5
            frames = int(duration * self.sample_rate)
            # Query device index if config is not default
            dev_idx = None
            if self.device != "default":
                try:
                    dev_idx = int(self.device)
                except ValueError:
                    # Lookup device name
                    devices = sd.query_devices()
                    for idx, dev in enumerate(devices):
                        if self.device in dev['name']:
                            dev_idx = idx
                            break

            recording = sd.rec(
                frames,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32',
                device=dev_idx
            )
            sd.wait()  # Wait until the recording is finished
            return SensorResult(success=True, data={
                "audio_data": recording.tolist(),
                "sample_rate": self.sample_rate,
                "channels": self.channels
            })
        except Exception as e:
            logger.error(f"Microphone capture failed: {e}")
            return SensorResult(success=False, error=str(e))
