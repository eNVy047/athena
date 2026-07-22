import logging
import json
import time
from typing import Optional

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if setup is called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | [%(name)s] | %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

class StructuredLogger:
    """Emits logs with required structured fields: timestamp, request_id, session_id, component, latency, status, error."""
    
    def __init__(self, component: str):
        self.logger = setup_logger(component)
        self.component = component

    def log(self, level: int, message: str, request_id: str = "", session_id: str = "", 
            latency: float = 0.0, status: str = "OK", error: Optional[str] = None, **kwargs):
            
        log_data = {
            "timestamp": time.time(),
            "request_id": request_id,
            "session_id": session_id,
            "component": self.component,
            "latency": latency,
            "status": status,
            "message": message
        }
        
        if error:
            log_data["error"] = error
            
        log_data.update(kwargs)
        
        # Log as structured JSON string
        self.logger.log(level, json.dumps(log_data))

    def info(self, message: str, **kwargs):
        self.log(logging.INFO, message, **kwargs)

    def error(self, message: str, error: str, **kwargs):
        self.log(logging.ERROR, message, error=error, status="FAILED", **kwargs)
        
    def warning(self, message: str, **kwargs):
        self.log(logging.WARNING, message, **kwargs)
        
    def debug(self, message: str, **kwargs):
        self.log(logging.DEBUG, message, **kwargs)
