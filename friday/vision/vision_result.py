from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from friday.vision.vision_models import VisualEntity, SceneUnderstanding, DocumentLayout

@dataclass
class VisionResult:
    """Standardized result containing all semantic understanding of an image."""
    success: bool
    source_sensor: str
    
    # Semantic outputs
    scene: Optional[SceneUnderstanding] = None
    caption: Optional[str] = None
    entities: List[VisualEntity] = field(default_factory=list)
    document_layout: Optional[DocumentLayout] = None
    extracted_text: Optional[str] = None
    
    # Error/Metadata
    error: Optional[str] = None
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
