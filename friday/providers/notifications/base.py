from abc import abstractmethod
from friday.providers.base.provider import Provider

class NotificationsProvider(Provider):
    @abstractmethod
    async def send_notification(self, title: str, body: str) -> None:
        """Sends system notification."""
        pass
