from enum import Enum
from dataclasses import dataclass
from typing import Optional

class HealthStatus(Enum):
    READY = "READY"
    STARTING = "STARTING"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    STOPPED = "STOPPED"

@dataclass
class HealthCheckResult:
    component: str
    status: HealthStatus
    message: Optional[str] = None
    latency_ms: float = 0.0
