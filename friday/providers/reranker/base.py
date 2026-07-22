from abc import abstractmethod
from typing import List, Tuple
from friday.providers.base.provider import Provider

class RerankerProvider(Provider):
    @abstractmethod
    async def rerank(self, query: str, documents: List[str], top_n: int = 5) -> List[Tuple[str, float, int]]:
        """Reranks documents relative to a query. Returns list of (document, score, index)."""
        pass
