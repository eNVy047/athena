import time
from typing import List, Optional
from friday.memory.memory_models import MemoryType, RetrievedMemory, MemorySearchQuery
from friday.memory.memory_search import MemorySearch
from friday.memory.memory_ranker import MemoryRanker
from friday.memory.memory_router import MemoryRouter


class MemoryRetriever:
    def __init__(
        self, router: MemoryRouter, search_engine: MemorySearch, ranker: MemoryRanker
    ):
        self.router = router
        self.search = search_engine
        self.ranker = ranker

    async def retrieve(
        self,
        query: str,
        limit: int = 5,
        memory_types: Optional[List[MemoryType]] = None,
    ) -> List[RetrievedMemory]:
        """Retrieves and ranks memories matching the query."""
        all_memories = self.router.retrieve_all(memory_types)
        if not all_memories:
            return []

        search_query = MemorySearchQuery(
            query=query, limit=limit, memory_types=memory_types
        )
        candidates = await self.search.hybrid_search(all_memories, search_query)

        # Update access recency timestamp on retrieved memory entries
        now = time.time()
        for c in candidates:
            c.entry.recency = now
            self.router.route_store(c.entry)

        return self.ranker.rank(candidates)
