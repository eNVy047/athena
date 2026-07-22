from abc import abstractmethod
from typing import List, Dict, Any
from friday.providers.base.provider import Provider

class EmailProvider(Provider):
    @abstractmethod
    async def send_email(self, recipient: str, subject: str, body: str) -> None:
        """Sends an email."""
        pass

    @abstractmethod
    async def read_emails(self, folder: str = "INBOX", limit: int = 5) -> List[Dict[str, Any]]:
        """Reads incoming emails."""
        pass
