import math
from typing import List, Tuple, Dict
from friday.knowledge.embeddings import EmbeddingEngine

class KnowledgeIndex:
    def __init__(self, embedding_engine: EmbeddingEngine):
        self.embedding_engine = embedding_engine
        self.documents: List[Tuple[str, List[float]]] = []

    async def add_document(self, text: str):
        vector = await self.embedding_engine.get_embedding(text)
        self.documents.append((text, vector))

    async def search_similar(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Performs cosine similarity search over indexed document chunks."""
        query_vector = await self.embedding_engine.get_embedding(query)
        
        results = []
        for text, doc_vector in self.documents:
            # Cosine similarity calculation
            dot_product = sum(q * d for q, d in zip(query_vector, doc_vector))
            q_norm = math.sqrt(sum(q * q for q in query_vector))
            d_norm = math.sqrt(sum(d * d for d in doc_vector))
            
            similarity = dot_product / (q_norm * d_norm) if q_norm and d_norm else 0.0
            results.append((text, similarity))
            
        # Sort by highest similarity
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
