from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class ProviderExecutionContext:
    session_id: str
    user_id: str
    trace_id: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)
