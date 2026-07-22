from abc import abstractmethod
from typing import Dict, Any
from friday.providers.base.provider import Provider

class WeatherProvider(Provider):
    @abstractmethod
    async def get_weather(self, location: str) -> Dict[str, Any]:
        """Gets current weather forecast for a location."""
        pass
