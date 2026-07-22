from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class AgentState:
    is_busy: bool = False
    current_task_id: str = ""
    status: str = "IDLE"  # IDLE, WORKING, PAUSED, ERROR
    metadata: Dict[str, Any] = field(default_factory=dict)
