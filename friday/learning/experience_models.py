from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import time

@dataclass
class Experience:
    """Represents a discrete historical event, workflow, or interaction."""
    id: str
    type: str # 'workflow', 'action', 'observation', 'correction'
    timestamp: float = field(default_factory=time.time)
    
    # Context
    trigger: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Outcomes
    success: bool = True
    result_summary: str = ""
    error_message: Optional[str] = None
    
    # Reflection hooks
    lessons_learned: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "timestamp": self.timestamp,
            "trigger": self.trigger,
            "parameters": self.parameters,
            "success": self.success,
            "result_summary": self.result_summary,
            "error_message": self.error_message,
            "lessons_learned": self.lessons_learned
        }
