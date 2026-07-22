from abc import abstractmethod
from friday.providers.base.provider import Provider

class MessagingProvider(Provider):
    @abstractmethod
    async def send_message(self, chat_id: str, text: str) -> None:
        """Sends an instant message to a specific chat ID."""
        pass
