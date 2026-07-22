from __future__ import annotations

from enum import Enum

class AgentStatus(str, Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    PAUSED = "paused"
    INTERRUPTED = "interrupted"
