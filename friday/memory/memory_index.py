import logging
from typing import List
from friday.memory.memory_models import MemoryEntry
from friday.memory.memory_embeddings import MemoryEmbeddingEngine

logger = logging.getLogger("friday-agent")


class MemoryIndex:
    def __init__(self, embedding_engine: MemoryEmbeddingEngine):
        self.embedding_engine = embedding_engine

    async def index_entry(self, entry: MemoryEntry) -> None:
        """Computes and assigns vector embedding for a memory entry if not present."""
        if not entry.embedding:
            try:
                entry.embedding = await self.embedding_engine.get_embedding(
                    entry.content
                )
            except Exception as e:
                logger.error(f"[MemoryIndex] Failed to generate embedding: {e}")

    async def index_entries(self, entries: List[MemoryEntry]) -> None:
        """Batch indexes multiple entries."""
        unindexed = [e for e in entries if not e.embedding]
        if not unindexed:
            return

        try:
            texts = [e.content for e in unindexed]
            embeddings = await self.embedding_engine.get_embeddings(texts)
            for entry, emb in zip(unindexed, embeddings):
                entry.embedding = emb
        except Exception as e:
            logger.error(
                f"[MemoryIndex] Batch indexing failed: {e}. Indexing one by one."
            )
            for entry in unindexed:
                await self.index_entry(entry)
