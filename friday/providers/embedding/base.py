from abc import abstractmethod
from typing import List
from friday.providers.base.provider import Provider

class EmbeddingProvider(Provider):
    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        """Generates embedding vector for text."""
        pass

    @abstractmethod
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embedding vectors for multiple texts."""
        pass
