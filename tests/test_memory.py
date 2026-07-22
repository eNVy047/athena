import os
import shutil
import tempfile
import asyncio
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from friday.memory.memory_models import MemoryEntry, MemoryType, Relationship, RetrievedMemory
from friday.memory.memory_store import SqliteMemoryStore
from friday.memory.memory_embeddings import MemoryEmbeddingEngine
from friday.memory.memory_search import MemorySearch
from friday.memory.memory_ranker import MemoryRanker
from friday.memory.memory_importance import MemoryImportanceScorer
from friday.memory.memory_decay import MemoryDecay
from friday.memory.memory_consolidation import MemoryConsolidation
from friday.memory.memory_relationships import MemoryRelationships
from friday.memory.memory_timeline import MemoryTimeline
from friday.memory.memory_cache import MemoryCache
from friday.memory.memory_snapshot import MemorySnapshotManager
from friday.memory.memory_manager import MemoryManager

@pytest.fixture
def temp_db():
    temp_dir = tempfile.mkdtemp()
    db_file = os.path.join(temp_dir, "test_memory.db")
    yield db_file
    shutil.rmtree(temp_dir)

def test_memory_models():
    entry = MemoryEntry(
        content="Testing memory model",
        memory_type=MemoryType.WORKING,
        importance=5.0
    )
    assert entry.content == "Testing memory model"
    assert entry.memory_type == MemoryType.WORKING
    assert entry.importance == 5.0

def test_sqlite_store(temp_db):
    store = SqliteMemoryStore(db_path=temp_db)
    store.initialize()
    
    entry = MemoryEntry(
        content="Local sqlite test",
        memory_type=MemoryType.EPISODIC,
        importance=7.0
    )
    store.add_memory(entry)
    
    mems = store.get_memories([MemoryType.EPISODIC])
    assert len(mems) == 1
    assert mems[0].content == "Local sqlite test"

@pytest.mark.asyncio
async def test_search_and_ranking():
    engine = MemoryEmbeddingEngine()
    search = MemorySearch(engine)
    ranker = MemoryRanker()
    
    entries = [
        MemoryEntry(id="1", content="Stark likes cheeseburgers", memory_type=MemoryType.SEMANTIC, importance=8.0),
        MemoryEntry(id="2", content="Python coding guidelines", memory_type=MemoryType.SHORT_TERM, importance=4.0)
    ]
    
    kw_res = search.keyword_search(entries, "cheeseburgers")
    assert len(kw_res) > 0
    assert kw_res[0][0].id == "1"
    
    retrieved = [RetrievedMemory(entry=e, score=0.9 if e.id == "1" else 0.2) for e in entries]
    ranked = ranker.rank(retrieved)
    assert ranked[0].entry.id == "1"

def test_importance_scorer():
    scorer = MemoryImportanceScorer()
    score = scorer.calculate_score("Always use python for AI work", {"category": "general"})
    # "Always" and "python" trigger rules, boosting score
    assert score > 5.0

def test_decay():
    decay = MemoryDecay(forgetting_threshold=3.0)
    entry = MemoryEntry(
        content="Decay me",
        memory_type=MemoryType.SHORT_TERM,
        importance=2.0,
        recency=0.0 # Way in the past
    )
    
    kept, forgotten = decay.process_decay_and_forget([entry])
    assert len(forgotten) == 1
    assert len(kept) == 0

@pytest.mark.asyncio
async def test_consolidation():
    engine = MemoryEmbeddingEngine()
    search = MemorySearch(engine)
    consolidation = MemoryConsolidation(search, similarity_threshold=0.9)
    
    emb = [0.1] * 128
    entry1 = MemoryEntry(id="1", content="Duplicate test fact", memory_type=MemoryType.SHORT_TERM, importance=7.0, embedding=emb)
    entry2 = MemoryEntry(id="2", content="Duplicate test fact", memory_type=MemoryType.SHORT_TERM, importance=4.0, embedding=emb)
    
    updated, to_delete = await consolidation.consolidate([entry1, entry2])
    assert "2" in to_delete
    assert len(updated) == 1
    # Check promotion to Semantic because importance was 7.0 (>=6.5)
    assert updated[0].memory_type == MemoryType.SEMANTIC

def test_relationships():
    rel_builder = MemoryRelationships()
    entry1 = MemoryEntry(id="1", content="Narayan loves Python coding", memory_type=MemoryType.EPISODIC)
    entry2 = MemoryEntry(id="2", content="Python is highly recommended", memory_type=MemoryType.SEMANTIC)
    
    rels = rel_builder.extract_relationships(entry1, [entry2])
    assert len(rels) == 1
    assert rels[0].relation_type == "entity_overlap"

def test_timeline():
    timeline = MemoryTimeline()
    entry1 = MemoryEntry(content="Conv 1", memory_type=MemoryType.CONVERSATION, created_at=100.0)
    entry2 = MemoryEntry(content="Conv 2", memory_type=MemoryType.CONVERSATION, created_at=200.0)
    
    sorted_timeline = timeline.get_chronological_sequence([entry1, entry2])
    assert sorted_timeline[0].content == "Conv 2"

@pytest.mark.asyncio
async def test_memory_manager_e2e(temp_db):
    config = {
        "SQLITE_STORAGE_DB": temp_db,
        "cache_enabled": True,
        "cache_ttl": 10.0
    }
    
    manager = MemoryManager(config=config)
    manager.initialize(session_id="test_session")
    
    # Store memory
    entry = MemoryEntry(
        content="I prefer Pytest for automated unit testing.",
        memory_type=MemoryType.SHORT_TERM
    )
    await manager.store_memory(entry)
    
    # Retrieve/Prefetch memory context
    context = await manager.prefetch("Pytest")
    assert "Pytest" in context.formatted
    
    # Run sync turn
    await manager.sync_turn("What is my favorite framework?", "You prefer Pytest.")
    
    # Test consolidation
    await manager.consolidate_memories()
    
    # Test decay
    await manager.apply_decay_and_forgetting()
    
    manager.shutdown()
