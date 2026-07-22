from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class PluginContext:
    plugin_id: str
    session_id: str
    config: Dict[str, Any] = field(default_factory=dict)
    sandbox_mode: bool = True
