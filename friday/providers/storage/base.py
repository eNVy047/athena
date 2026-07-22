from abc import abstractmethod
from typing import Dict, Any, Optional
from friday.providers.base.provider import Provider

class StorageProvider(Provider):
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Gets value from storage."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, expire_seconds: Optional[int] = None) -> None:
        """Sets value in storage."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Removes key from storage."""
        pass
