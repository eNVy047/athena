from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict

# Runtime Event Names
JOB_STARTED = "runtime.job_started"
JOB_COMPLETED = "runtime.job_completed"
JOB_FAILED = "runtime.job_failed"
WORKER_CREATED = "runtime.worker_created"
WORKER_STOPPED = "runtime.worker_stopped"
QUEUE_EMPTY = "runtime.queue_empty"
QUEUE_OVERFLOW = "runtime.queue_overflow"
CHECKPOINT_CREATED = "runtime.checkpoint_created"
RECOVERY_STARTED = "runtime.recovery_started"
RECOVERY_COMPLETED = "runtime.recovery_completed"

@dataclass
class RuntimeEvent:
    """Base event model for Friday runtime operations."""
    name: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
