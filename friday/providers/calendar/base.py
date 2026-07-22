from abc import abstractmethod
from typing import List, Dict, Any
from friday.providers.base.provider import Provider

class CalendarProvider(Provider):
    @abstractmethod
    async def get_events(self, start_time: str, end_time: str) -> List[Dict[str, Any]]:
        """Retrieves calendar events between two time periods."""
        pass

    @abstractmethod
    async def create_event(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a calendar event."""
        pass
