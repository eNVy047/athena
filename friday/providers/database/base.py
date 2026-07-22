from abc import abstractmethod
from typing import List, Dict, Any
from friday.providers.base.provider import Provider

class DatabaseProvider(Provider):
    @abstractmethod
    async def execute_query(self, query: str, params: List[Any] = None) -> List[Dict[str, Any]]:
        """Executes a SQL or database query and returns rows as dictionaries."""
        pass
