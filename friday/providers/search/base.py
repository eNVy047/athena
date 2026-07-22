from abc import abstractmethod
from typing import List, Dict, Any
from friday.providers.base.provider import Provider

class SearchProvider(Provider):
    @abstractmethod
    async def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Performs search and returns a structured list of results."""
        pass
