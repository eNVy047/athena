from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class BrowserBounds:
    x: int
    y: int
    width: int
    height: int

@dataclass
class BrowserElement:
    selector: str
    tag_name: str
    inner_text: str
    is_visible: bool
    is_interactive: bool
    bounds: Optional[BrowserBounds] = None
    attributes: Dict[str, str] = field(default_factory=dict)

@dataclass
class BrowserResult:
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
