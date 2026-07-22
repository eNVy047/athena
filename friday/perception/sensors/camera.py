import logging
import cv2
from typing import Dict, Any
from friday.perception.sensor import Sensor
from friday.perception.sensor_metadata import SensorMetadata, SensorStatus
from friday.perception.sensor_context import SensorContext
from friday.perception.sensor_result import SensorResult

logger = logging.getLogger(__name__)

class CameraSensor(Sensor):
    def __init__(self):
        metadata = SensorMetadata(
            name="camera",
            description="Observes feed from webcam/camera using OpenCV",
            version="1.0.0",
            capabilities=["vision.frame_capture"],
            required_permissions=[]
        )
        super().__init__(metadata)
        self.cap = None
        self.camera_index = 0
        self.width = 1280
        self.height = 720

    async def initialize(self, context: SensorContext) -> None:
        await super().initialize(context)
        self.camera_index = int(self.context.config.get("CAMERA_INDEX", 0))
        self.width = int(self.context.config.get("CAMERA_WIDTH", 1280))
        self.height = int(self.context.config.get("CAMERA_HEIGHT", 720))

    async def start(self) -> None:
        await super().start()
        self._open_camera()

    def _open_camera(self) -> None:
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        except Exception as e:
            logger.error(f"Failed to open camera: {e}")
            self.status = SensorStatus.ERROR

    async def pause(self) -> None:
        await super().pause()

    async def resume(self) -> None:
        await super().resume()
        if not self.cap or not self.cap.isOpened():
            self._open_camera()

    async def stop(self) -> None:
        await super().stop()
        if self.cap:
            self.cap.release()
            self.cap = None

    async def health_check(self) -> bool:
        if not self.cap or not self.cap.isOpened():
            return False
        return await super().health_check()

    async def observe(self) -> SensorResult:
        if self.status != SensorStatus.RUNNING:
            return SensorResult(success=False, error="Sensor not running")

        if not self.cap or not self.cap.isOpened():
            self._open_camera()
            if not self.cap or not self.cap.isOpened():
                return SensorResult(success=False, error="Camera device unavailable")

        ret, frame = self.cap.read()
        if not ret:
            # Try to reconnect
            self.cap.release()
            self._open_camera()
            return SensorResult(success=False, error="Failed to grab frame from camera")

        # Convert frame to jpeg bytes
        _, jpeg = cv2.imencode('.jpg', frame)
        return SensorResult(success=True, data={
            "bytes": jpeg.tobytes(),
            "width": self.width,
            "height": self.height
        })
