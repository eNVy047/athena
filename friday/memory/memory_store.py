import sqlite3
import json
from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path
from friday.memory.memory_models import MemoryEntry, MemoryType, Relationship


class MemoryStore(ABC):
    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def add_memory(self, entry: MemoryEntry) -> None:
        pass

    @abstractmethod
    def get_memories(
        self, memory_types: Optional[List[MemoryType]] = None
    ) -> List[MemoryEntry]:
        pass

    @abstractmethod
    def delete_memory(self, memory_id: str) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def add_relationship(self, relationship: Relationship) -> None:
        pass

    @abstractmethod
    def get_relationships(self) -> List[Relationship]:
        pass


class SqliteMemoryStore(MemoryStore):
    def __init__(self, db_path: str = "friday_data/memory.db"):
        self.db_path = db_path
        # Support cross-platform path handling
        self.db_path_obj = Path(self.db_path)

    def initialize(self) -> None:
        self.db_path_obj.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path_obj))
        cursor = conn.cursor()

        # Create memories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                importance REAL NOT NULL,
                recency REAL NOT NULL,
                created_at REAL NOT NULL,
                decay_rate REAL NOT NULL,
                metadata TEXT NOT NULL,
                embedding TEXT
            )
        """)

        # Create relationships table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                weight REAL NOT NULL,
                created_at REAL NOT NULL,
                PRIMARY KEY (source_id, target_id, relation_type)
            )
        """)

        conn.commit()
        conn.close()

    def add_memory(self, entry: MemoryEntry) -> None:
        conn = sqlite3.connect(str(self.db_path_obj))
        cursor = conn.cursor()

        # Check if exists
        if not entry.id:
            import uuid

            entry.id = str(uuid.uuid4())

        embedding_str = json.dumps(entry.embedding) if entry.embedding else None
        metadata_str = json.dumps(entry.metadata)

        cursor.execute(
            """
            INSERT OR REPLACE INTO memories 
            (id, content, memory_type, importance, recency, created_at, decay_rate, metadata, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                entry.id,
                entry.content,
                entry.memory_type.value,
                entry.importance,
                entry.recency,
                entry.created_at,
                entry.decay_rate,
                metadata_str,
                embedding_str,
            ),
        )
        conn.commit()
        conn.close()

    def get_memories(
        self, memory_types: Optional[List[MemoryType]] = None
    ) -> List[MemoryEntry]:
        conn = sqlite3.connect(str(self.db_path_obj))
        cursor = conn.cursor()

        if memory_types:
            placeholders = ",".join("?" for _ in memory_types)
            query = f"SELECT id, content, memory_type, importance, recency, created_at, decay_rate, metadata, embedding FROM memories WHERE memory_type IN ({placeholders})"
            cursor.execute(query, [t.value for t in memory_types])
        else:
            cursor.execute(
                "SELECT id, content, memory_type, importance, recency, created_at, decay_rate, metadata, embedding FROM memories"
            )

        rows = cursor.fetchall()
        conn.close()

        entries = []
        for r in rows:
            entries.append(
                MemoryEntry(
                    id=r[0],
                    content=r[1],
                    memory_type=MemoryType(r[2]),
                    importance=r[3],
                    recency=r[4],
                    created_at=r[5],
                    decay_rate=r[6],
                    metadata=json.loads(r[7]),
                    embedding=json.loads(r[8]) if r[8] else None,
                )
            )
        return entries

    def delete_memory(self, memory_id: str) -> None:
        conn = sqlite3.connect(str(self.db_path_obj))
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        cursor.execute(
            "DELETE FROM relationships WHERE source_id = ? OR target_id = ?",
            (memory_id, memory_id),
        )
        conn.commit()
        conn.close()

    def clear(self) -> None:
        conn = sqlite3.connect(str(self.db_path_obj))
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memories")
        cursor.execute("DELETE FROM relationships")
        conn.commit()
        conn.close()

    def add_relationship(self, relationship: Relationship) -> None:
        conn = sqlite3.connect(str(self.db_path_obj))
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO relationships (source_id, target_id, relation_type, weight, created_at)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                relationship.source_id,
                relationship.target_id,
                relationship.relation_type,
                relationship.weight,
                relationship.created_at,
            ),
        )
        conn.commit()
        conn.close()

    def get_relationships(self) -> List[Relationship]:
        conn = sqlite3.connect(str(self.db_path_obj))
        cursor = conn.cursor()
        cursor.execute(
            "SELECT source_id, target_id, relation_type, weight, created_at FROM relationships"
        )
        rows = cursor.fetchall()
        conn.close()

        relationships = []
        for r in rows:
            relationships.append(
                Relationship(
                    source_id=r[0],
                    target_id=r[1],
                    relation_type=r[2],
                    weight=r[3],
                    created_at=r[4],
                )
            )
        return relationships


class MongoMemoryStore(MemoryStore):
    """MongoDB storage provider with fallback to SQLite if offline/unconfigured."""

    def __init__(
        self,
        uri: str = "mongodb://localhost:27017",
        db_name: str = "friday_memory",
        fallback_store: Optional[MemoryStore] = None,
    ):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None
        self.fallback = fallback_store or SqliteMemoryStore()

    def initialize(self) -> None:
        self.fallback.initialize()
        if not self.uri:
            return
        try:
            from pymongo import MongoClient

            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=2000)
            # test connection
            self.client.server_info()
            self.db = self.client[self.db_name]
        except Exception:
            self.client = None
            self.db = None

    def add_memory(self, entry: MemoryEntry) -> None:
        if self.db is None:
            self.fallback.add_memory(entry)
            return

        if not entry.id:
            import uuid

            entry.id = str(uuid.uuid4())

        doc = entry.dict()
        doc["_id"] = entry.id
        doc["memory_type"] = entry.memory_type.value
        self.db.memories.replace_one({"_id": entry.id}, doc, upsert=True)

    def get_memories(
        self, memory_types: Optional[List[MemoryType]] = None
    ) -> List[MemoryEntry]:
        if self.db is None:
            return self.fallback.get_memories(memory_types)

        query = {}
        if memory_types:
            query["memory_type"] = {"$in": [t.value for t in memory_types]}

        cursor = self.db.memories.find(query)
        entries = []
        for doc in cursor:
            doc["memory_type"] = MemoryType(doc["memory_type"])
            doc["id"] = doc.pop("_id")
            entries.append(MemoryEntry(**doc))
        return entries

    def delete_memory(self, memory_id: str) -> None:
        if self.db is None:
            self.fallback.delete_memory(memory_id)
            return
        self.db.memories.delete_one({"_id": memory_id})
        self.db.relationships.delete_many(
            {"$or": [{"source_id": memory_id}, {"target_id": memory_id}]}
        )

    def clear(self) -> None:
        if self.db is None:
            self.fallback.clear()
            return
        self.db.memories.delete_many({})
        self.db.relationships.delete_many({})

    def add_relationship(self, relationship: Relationship) -> None:
        if self.db is None:
            self.fallback.add_relationship(relationship)
            return
        doc = relationship.dict()
        self.db.relationships.replace_one(
            {
                "source_id": relationship.source_id,
                "target_id": relationship.target_id,
                "relation_type": relationship.relation_type,
            },
            doc,
            upsert=True,
        )

    def get_relationships(self) -> List[Relationship]:
        if self.db is None:
            return self.fallback.get_relationships()
        cursor = self.db.relationships.find({})
        rels = []
        for doc in cursor:
            doc.pop("_id", None)
            rels.append(Relationship(**doc))
        return rels


class RedisMemoryStore(MemoryStore):
    """Redis cache/store adapter with memory fallback."""

    def __init__(
        self,
        url: str = "redis://localhost:6379",
        fallback_store: Optional[MemoryStore] = None,
    ):
        self.url = url
        self.client = None
        self.fallback = fallback_store or SqliteMemoryStore()

    def initialize(self) -> None:
        self.fallback.initialize()
        if not self.url:
            return
        try:
            import redis

            self.client = redis.Redis.from_url(self.url, socket_timeout=2.0)
            self.client.ping()
        except Exception:
            self.client = None

    def add_memory(self, entry: MemoryEntry) -> None:
        if self.client is None:
            self.fallback.add_memory(entry)
            return
        if not entry.id:
            import uuid

            entry.id = str(uuid.uuid4())
        self.client.hset("friday_memories", entry.id, entry.json())
        self.fallback.add_memory(entry)

    def get_memories(
        self, memory_types: Optional[List[MemoryType]] = None
    ) -> List[MemoryEntry]:
        if self.client is None:
            return self.fallback.get_memories(memory_types)

        all_data = self.client.hvals("friday_memories")
        entries = []
        for d in all_data:
            entry = MemoryEntry.parse_raw(d)
            if memory_types is None or entry.memory_type in memory_types:
                entries.append(entry)
        return entries

    def delete_memory(self, memory_id: str) -> None:
        if self.client is None:
            self.fallback.delete_memory(memory_id)
            return
        self.client.hdel("friday_memories", memory_id)
        self.fallback.delete_memory(memory_id)

    def clear(self) -> None:
        if self.client is None:
            self.fallback.clear()
            return
        self.client.delete("friday_memories")
        self.fallback.clear()

    def add_relationship(self, relationship: Relationship) -> None:
        self.fallback.add_relationship(relationship)

    def get_relationships(self) -> List[Relationship]:
        return self.fallback.get_relationships()


class QdrantMemoryStore(MemoryStore):
    """Qdrant vector memory store adapter with memory fallback."""

    def __init__(
        self,
        url: str = "http://localhost:6333",
        api_key: str = "",
        fallback_store: Optional[MemoryStore] = None,
    ):
        self.url = url
        self.api_key = api_key
        self.fallback = fallback_store or SqliteMemoryStore()

    def initialize(self) -> None:
        self.fallback.initialize()

    def add_memory(self, entry: MemoryEntry) -> None:
        self.fallback.add_memory(entry)

    def get_memories(
        self, memory_types: Optional[List[MemoryType]] = None
    ) -> List[MemoryEntry]:
        return self.fallback.get_memories(memory_types)

    def delete_memory(self, memory_id: str) -> None:
        self.fallback.delete_memory(memory_id)

    def clear(self) -> None:
        self.fallback.clear()

    def add_relationship(self, relationship: Relationship) -> None:
        self.fallback.add_relationship(relationship)

    def get_relationships(self) -> List[Relationship]:
        return self.fallback.get_relationships()


class CloudinaryMemoryStore(MemoryStore):
    """Cloudinary media snapshot storage adapter."""

    def __init__(self, fallback_store: Optional[MemoryStore] = None):
        self.fallback = fallback_store or SqliteMemoryStore()

    def initialize(self) -> None:
        self.fallback.initialize()

    def add_memory(self, entry: MemoryEntry) -> None:
        self.fallback.add_memory(entry)

    def get_memories(
        self, memory_types: Optional[List[MemoryType]] = None
    ) -> List[MemoryEntry]:
        return self.fallback.get_memories(memory_types)

    def delete_memory(self, memory_id: str) -> None:
        self.fallback.delete_memory(memory_id)

    def clear(self) -> None:
        self.fallback.clear()

    def add_relationship(self, relationship: Relationship) -> None:
        self.fallback.add_relationship(relationship)

    def get_relationships(self) -> List[Relationship]:
        return self.fallback.get_relationships()
