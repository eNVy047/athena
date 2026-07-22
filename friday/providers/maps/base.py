from abc import abstractmethod
from typing import Dict, Any
from friday.providers.base.provider import Provider

class MapsProvider(Provider):
    @abstractmethod
    async def get_directions(self, origin: str, destination: str) -> Dict[str, Any]:
        """Gets driving/walking directions between coordinates/locations."""
        pass
