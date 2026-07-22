from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

@dataclass
class BoundingBox:
    x_min: int
    y_min: int
    x_max: int
    y_max: int

@dataclass
class VisualEntity:
    """Represents a discrete object, text block, or UI element detected in an image."""
    label: str
    confidence: float
    box: Optional[BoundingBox] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class SceneUnderstanding:
    """High-level semantic understanding of a scene/image."""
    description: str
    environment_type: Optional[str] = None # e.g., 'office', 'desktop', 'outdoor'
    lighting_conditions: Optional[str] = None
    key_objects: List[str] = field(default_factory=list)
    detected_activities: List[str] = field(default_factory=list)

@dataclass
class DocumentLayout:
    """Understanding of a document or screen's layout."""
    title: Optional[str] = None
    text_blocks: List[VisualEntity] = field(default_factory=list)
    interactive_elements: List[VisualEntity] = field(default_factory=list)
    key_value_pairs: Dict[str, str] = field(default_factory=dict)
