from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import time

@dataclass
class VisionContext:
    """Contextual information for a vision processing request."""
    session_id: str
    source_sensor: str  # e.g., "camera", "screen"
    timestamp: float = field(default_factory=time.time)
    
    # Preprocessing constraints
    target_width: Optional[int] = None
    target_height: Optional[int] = None
    
    # Analysis preferences
    require_ocr: bool = True
    require_scene_understanding: bool = True
    require_face_analysis: bool = False
    
    metadata: Dict[str, Any] = field(default_factory=dict)
