from abc import ABC, abstractmethod
from typing import Dict, Set, Any, Optional
from pydantic import BaseModel

class CapabilityGraph(BaseModel):
    capabilities: Set[str] = set()
    metadata: Dict[str, Any] = {}

    def has(self, capability: str) -> bool:
        return capability in self.capabilities

    def require(self, capability: str) -> None:
        if not self.has(capability):
            raise RuntimeError(f"Missing required system capability: {capability}")

class PlatformCapabilities(BaseModel):
    has_browser: bool = False
    has_audio_input: bool = False
    has_audio_output: bool = False
    has_camera: bool = False
    has_notifications: bool = False
    has_secure_storage: bool = False
    has_terminal: bool = False
    hardware_acceleration: bool = False

class PlatformMetrics(BaseModel):
    cpu_usage_pct: float
    ram_usage_pct: float
    battery_pct: Optional[float] = None
    temperature_celsius: Optional[float] = None
    network_connected: bool

class SecureStorage(ABC):
    @abstractmethod
    async def get_secret(self, service: str, account: str) -> Optional[str]:
        pass

    @abstractmethod
    async def set_secret(self, service: str, account: str, secret: str) -> None:
        pass

class PlatformManager(ABC):
    @abstractmethod
    def get_os_name(self) -> str:
        pass

    @abstractmethod
    def get_capabilities(self) -> PlatformCapabilities:
        pass

    @abstractmethod
    def get_metrics(self) -> PlatformMetrics:
        pass
