from abc import abstractmethod
from typing import List, Dict, Any, Optional
from friday.providers.base.provider import Provider

class MemoryProvider(Provider):
    @abstractmethod
    async def add(self, text: str, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Stores a memory entry."""
        pass

    @abstractmethod
    async def search(self, query: str, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves memories matching a query."""
        pass

    @abstractmethod
    async def delete(self, memory_id: str) -> None:
        """Deletes a memory entry by ID."""
        pass
