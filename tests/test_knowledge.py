import pytest
from friday.knowledge.parser import DocumentParser
from friday.knowledge.chunker import TextChunker
from friday.knowledge.embeddings import MockEmbeddingEngine
from friday.knowledge.index import KnowledgeIndex
from friday.knowledge.retriever import KnowledgeRetriever

@pytest.mark.asyncio
async def test_knowledge_indexing_and_retrieval():
    # 1. Parse document content
    html_doc = "<html><body><h1>Stark Suit Protocols</h1><p>Mark 85 power level is at 100%.</p></body></html>"
    parsed_text = DocumentParser.parse_html(html_doc)
    assert parsed_text == "Stark Suit ProtocolsMark 85 power level is at 100%."
    
    # 2. Chunk text
    chunks = TextChunker.chunk_text(parsed_text, chunk_size=4, overlap=1)
    assert len(chunks) > 0
    
    # 3. Vector indexing and similarity retrieval
    mock_embeddings = MockEmbeddingEngine()
    index = KnowledgeIndex(embedding_engine=mock_embeddings)
    
    for chunk in chunks:
        await index.add_document(chunk)
        
    retriever = KnowledgeRetriever(index=index)
    results = await retriever.retrieve_context("Stark Suit Protocols", limit=1)
    
    assert len(results) == 1
    assert "Protocols" in results[0] or "Stark" in results[0]

@pytest.mark.asyncio
async def test_knowledge_e2e_agent():
    from friday.kernel.kernel import FridayKernel
    from friday.kernel.runtime import FridayAgent
    from pathlib import Path
    import shutil
    
    storage_root = Path(__file__).parent.parent / "friday" / "prompts" / "temp_knowledge_agent_test"
    kernel = FridayKernel(storage_root=storage_root)
    kernel.bootstrap()
    agent = FridayAgent(kernel=kernel)
    
    res_search = await agent.process_input("Search project documentation for MCP")
    assert "MCP" in res_search
    
    res_sum = await agent.process_input("Summarize README.md")
    assert "Friday OS is a production-grade" in res_sum
    
    kernel.shutdown()
    shutil.rmtree(storage_root, ignore_errors=True)

