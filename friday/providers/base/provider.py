from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.base.provider_health import ProviderHealthTracker

class Provider(ABC):
    def __init__(self, metadata: ProviderMetadata, config: Dict[str, Any]):
        self.metadata = metadata
        self.config = config
        self.is_connected = False
        self.health_tracker = ProviderHealthTracker()

    @abstractmethod
    async def initialize(self) -> None:
        """Initializes internal structures of the provider."""
        pass

    @abstractmethod
    async def connect(self) -> None:
        """Establishes connection to the external service/API."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Gracefully disconnects/cleans up resources."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Performs a self-check on the provider. Returns True if healthy, False otherwise."""
        pass
