from enum import Enum
from typing import Dict, Any, List

class SensorStatus(str, Enum):
    OFFLINE = "OFFLINE"
    INITIALIZED = "INITIALIZED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    ERROR = "ERROR"

class SensorMetadata:
    def __init__(
        self,
        name: str,
        description: str,
        version: str,
        capabilities: List[str],
        required_permissions: List[str]
    ):
        self.name = name
        self.description = description
        self.version = version
        self.capabilities = capabilities
        self.required_permissions = required_permissions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": self.capabilities,
            "required_permissions": self.required_permissions
        }
