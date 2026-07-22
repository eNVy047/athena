import logging
import json
from typing import Dict, Any

logger = logging.getLogger("audit")

class AuditLog:
    """Tracks critical system changes, plugin loads, and access events."""
    
    @staticmethod
    def record_event(event_type: str, actor: str, target: str, status: str, details: Dict[str, Any] = None):
        log_data = {
            "type": event_type,
            "actor": actor,
            "target": target,
            "status": status,
            "details": details or {}
        }
        logger.info(json.dumps(log_data))
