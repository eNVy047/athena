import logging
import time
import asyncio
from typing import List, Optional, Dict, Any
from friday.memory.memory_models import MemoryEntry, MemoryType, MemoryContext
from friday.memory.memory_store import SqliteMemoryStore
from friday.memory.memory_router import MemoryRouter
from friday.memory.memory_embeddings import MemoryEmbeddingEngine
from friday.memory.memory_index import MemoryIndex
from friday.memory.memory_search import MemorySearch
from friday.memory.memory_ranker import MemoryRanker
from friday.memory.memory_importance import MemoryImportanceScorer
from friday.memory.memory_decay import MemoryDecay
from friday.memory.memory_consolidation import MemoryConsolidation
from friday.memory.memory_relationships import MemoryRelationships
from friday.memory.memory_timeline import MemoryTimeline
from friday.memory.memory_cache import MemoryCache
from friday.memory.memory_events import MemoryEvents
from friday.memory.memory_context import MemoryContextFormatter
from friday.memory.memory_observer import MemoryObserver
from friday.memory.memory_scheduler import MemoryScheduler

logger = logging.getLogger("friday-agent")


class MemoryManager:
    """The central orchestrator for Friday's Human Memory System."""

    def __init__(
        self,
        config: Dict[str, Any],
        registry: Optional[Any] = None,
        stores: Optional[List[Any]] = None,
        embedding_engine: Optional[MemoryEmbeddingEngine] = None,
        event_bus: Optional[Any] = None,
    ) -> None:
        self.config = config
        self.registry = registry

        # 1. Setup swappable stores
        if not stores:
            sqlite_store = SqliteMemoryStore(
                config.get("SQLITE_STORAGE_DB", "friday_data/memory.db")
            )
            stores = [sqlite_store]
        self.stores = stores
        self.router = MemoryRouter(self.stores)

        # 2. Setup subsystems
        self.embedding_engine = embedding_engine or MemoryEmbeddingEngine(registry)
        self.index = MemoryIndex(self.embedding_engine)
        self.search = MemorySearch(self.embedding_engine)
        self.ranker = MemoryRanker()
        self.importance_scorer = MemoryImportanceScorer()
        self.decay = MemoryDecay()
        self.consolidation = MemoryConsolidation(self.search)
        self.relationships = MemoryRelationships()
        self.timeline = MemoryTimeline()
        self.cache = MemoryCache(
            enabled=config.get("cache_enabled", True), ttl=config.get("cache_ttl", 60.0)
        )
        self.events = MemoryEvents(event_bus)
        self.context_formatter = MemoryContextFormatter()
        self.observer = MemoryObserver(event_bus)
        self.observer.set_memory_manager(self)
        self.scheduler = MemoryScheduler(self)

    def initialize(self, session_id: str = "default_session", **kwargs) -> None:
        """Initializes all storage layers and starts scheduled background tasks."""
        for store in self.stores:
            store.initialize()
        self.observer.initialize()
        self.scheduler.start()
        logger.info("[MemoryManager] Human Memory System fully initialized.")

    async def prefetch(self, query: str) -> MemoryContext:
        """Prefetches memories relevant to the query, deduplicating and ranking them."""
        # 1. Check Cache
        cached = self.cache.get(query)
        if cached:
            return cached

        # 2. Retrieve memories using search & ranking
        all_memories = self.router.retrieve_all()
        if not all_memories:
            return MemoryContext()

        from friday.memory.memory_models import MemorySearchQuery

        search_query = MemorySearchQuery(query=query, limit=5)
        candidates = await self.search.hybrid_search(all_memories, search_query)

        # 3. Update access/recency timestamp
        now = time.time()
        for c in candidates:
            c.entry.recency = now
            self.router.route_store(c.entry)

        ranked = self.ranker.rank(candidates)

        # 4. Format Context
        context = self.context_formatter.format(ranked)

        # 5. Populate Cache
        self.cache.set(query, context)

        await self.events.publish_recalled(query, len(ranked))
        return context

    async def store_memory(self, entry: MemoryEntry) -> None:
        """Core process to score, index, extract relationships and persist a memory."""
        # 1. Score Importance
        entry.importance = self.importance_scorer.calculate_score(
            entry.content, entry.metadata
        )

        # 2. Compute Embedding Vector
        await self.index.index_entry(entry)

        # 3. Route & Save
        self.router.route_store(entry)

        # 4. Relate to other memories
        all_entries = self.router.retrieve_all()
        relations = self.relationships.extract_relationships(entry, all_entries)
        for r in relations:
            for store in self.stores:
                if hasattr(store, "add_relationship"):
                    store.add_relationship(r)

        # 5. Clear cache as state has changed
        self.cache.invalidate()

        # 6. Publish event
        await self.events.publish_stored(entry)

    async def sync_turn(
        self,
        user_msg: str,
        assistant_msg: str,
        extracted: Optional[List[MemoryEntry]] = None,
    ) -> None:
        """Process dialog turn to index conversation memory and extract new semantic memories."""
        # 1. Store conversation memory turn
        conv_content = f"User: {user_msg}\nAssistant: {assistant_msg}"
        conv_entry = MemoryEntry(
            content=conv_content,
            memory_type=MemoryType.CONVERSATION,
            metadata={"category": "conversation"},
        )
        await self.store_memory(conv_entry)

        # 2. Store extracted semantic facts
        if extracted:
            for entry in extracted:
                await self.store_memory(entry)

    async def consolidate_memories(self) -> None:
        """Consolidates short-term/episodic memories."""
        all_entries = self.router.retrieve_all()
        updated, to_delete = await self.consolidation.consolidate(all_entries)

        for entry in updated:
            self.router.route_store(entry)

        for d_id in to_delete:
            self.router.route_delete(d_id)

    async def apply_decay_and_forgetting(self) -> None:
        """Applies Ebbinghaus forgetting curve decay to stored memories."""
        all_entries = self.router.retrieve_all()
        kept, forgotten = self.decay.process_decay_and_forget(all_entries)

        # Save decayed kept entries
        for entry in kept:
            self.router.route_store(entry)

        # Remove forgotten entries
        for entry in forgotten:
            if entry.id:
                self.router.route_delete(entry.id)
                logger.info(f"[MemoryDecay] Memory forgotten: {entry.content}")

    def shutdown(self) -> None:
        """Stops background threads / async loops."""
        asyncio.create_task(self.scheduler.stop())
        logger.info("[MemoryManager] Human Memory System shut down.")

    def prefetch_sync(self, query: str) -> MemoryContext:
        """Synchronous wrapper to run async prefetch using ThreadPoolExecutor to prevent blocking the main loop."""
        import concurrent.futures
        import asyncio

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, self.prefetch(query))
            return future.result()
