from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class PluginResult:
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
