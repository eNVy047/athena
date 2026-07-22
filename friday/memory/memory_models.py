from __future__ import annotations

import time
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    WORKING = "working"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    PROCEDURAL = "procedural"
    CONVERSATION = "conversation"
    WORLD = "world"
    SKILL = "skill"
    REFLECTION = "reflection"


class MemoryEntry(BaseModel):
    id: Optional[str] = None
    content: str
    memory_type: MemoryType
    importance: float = 0.0  # 0.0 to 10.0
    recency: float = Field(
        default_factory=time.time
    )  # Last access time / creation time
    created_at: float = Field(default_factory=time.time)
    decay_rate: float = 0.01  # Default decay rate
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None


class Relationship(BaseModel):
    source_id: str
    target_id: str
    relation_type: str
    weight: float = 1.0
    created_at: float = Field(default_factory=time.time)


class RetrievedMemory(BaseModel):
    entry: MemoryEntry
    score: float = 1.0  # Combined score of relevance, recency, and importance


class MemoryContext(BaseModel):
    retrieved: List[RetrievedMemory] = Field(default_factory=list)
    formatted: str = ""


class MemorySearchQuery(BaseModel):
    query: str
    memory_types: Optional[List[MemoryType]] = None
    limit: int = 5
    min_score: float = 0.0
    hybrid_weight: float = 0.5  # Weight between keyword and embedding search


class MemoryConfig:
    def __init__(
        self,
        enabled: bool = True,
        provider: str = "builtin",
        storage_path: str = "friday_data/memory.db",
        max_memories: int = 10,
        cache_enabled: bool = True,
        cache_ttl: float = 60.0,
        ranking_limit: int = 5,
    ):
        self.enabled = enabled
        self.provider = provider
        self.storage_path = storage_path
        self.max_memories = max_memories
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl
        self.ranking_limit = ranking_limit

    @classmethod
    def from_env(cls):
        import os

        return cls(
            enabled=os.getenv("MEMORY_ENABLED", "true").lower() == "true",
            provider=os.getenv("MEMORY_PROVIDER", "builtin"),
            storage_path=os.getenv("SQLITE_STORAGE_DB", "friday_data/memory.db"),
        )
