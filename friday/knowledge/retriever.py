from typing import List
from friday.knowledge.index import KnowledgeIndex

class KnowledgeRetriever:
    def __init__(self, index: KnowledgeIndex):
        self.index = index

    async def retrieve_context(self, query: str, limit: int = 2) -> List[str]:
        results = await self.index.search_similar(query, top_k=limit)
        return [text for text, score in results]
