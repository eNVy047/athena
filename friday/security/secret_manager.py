import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class SecretManager:
    """Manages secure access to API keys and prevents them from leaking."""
    
    def __init__(self):
        self._secrets = {}
        
    def load_from_env(self):
        for k, v in os.environ.items():
            if "API_KEY" in k or "SECRET" in k or "TOKEN" in k:
                self._secrets[k] = v
                
    def get_secret(self, key: str) -> Optional[str]:
        return self._secrets.get(key)
        
    def redact_logs(self, message: str) -> str:
        redacted = message
        for val in self._secrets.values():
            if val and len(val) > 4:
                redacted = redacted.replace(val, "********")
        return redacted
