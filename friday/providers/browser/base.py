from abc import abstractmethod
from typing import Dict, Any, List
from friday.providers.base.provider import Provider

class BrowserProvider(Provider):
    @abstractmethod
    async def navigate_to(self, url: str) -> None:
        """Navigates browser to the target URL."""
        pass

    @abstractmethod
    async def get_page_content(self) -> str:
        """Returns the DOM/HTML content of the active page."""
        pass
