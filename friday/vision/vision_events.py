from dataclasses import dataclass
from typing import Optional, Dict, Any
from friday.events.event_types import Event

VISION_FRAME_CAPTURED = "vision.frame_captured"
VISION_SCENE_ANALYZED = "vision.scene_analyzed"
VISION_ENTITY_DETECTED = "vision.entity_detected"
VISION_DOCUMENT_ANALYZED = "vision.document_analyzed"
VISION_TEXT_EXTRACTED = "vision.text_extracted"
VISION_ERROR = "vision.error"

@dataclass
class VisionEvent(Event):
    """Base event for vision system."""
    session_id: str = ""
    source_sensor: str = ""
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class FrameCapturedEvent(VisionEvent):
    """Fired when a raw frame is captured."""
    image_data: bytes = b""
    width: int = 0
    height: int = 0

@dataclass
class SceneAnalyzedEvent(VisionEvent):
    """Fired when a scene is semantically understood."""
    description: str = ""
    environment: Optional[str] = None
