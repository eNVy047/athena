from typing import Protocol, List

class EmbeddingEngine(Protocol):
    async def get_embedding(self, text: str) -> List[float]:
        ...

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        ...

class MockEmbeddingEngine:
    def _to_vector(self, text: str) -> List[float]:
        # Simple character frequency vector (26 elements) to provide real cosine similarity
        vec = [0.1] * 26
        for char in text.lower():
            if 'a' <= char <= 'z':
                vec[ord(char) - ord('a')] += 1.0
        return vec

    async def get_embedding(self, text: str) -> List[float]:
        return self._to_vector(text)

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self._to_vector(t) for t in texts]



