import time
from typing import Dict, Any

class ProviderEvent:
    def __init__(self, provider_name: str, category: str, event_type: str, details: Dict[str, Any] = None):
        self.provider_name = provider_name
        self.category = category
        self.event_type = event_type
        self.timestamp = time.time()
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_name": self.provider_name,
            "category": self.category,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "details": self.details
        }
