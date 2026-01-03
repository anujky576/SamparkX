#!/usr/bin/env python3
"""Test script to verify the complete pipeline without API calls."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.logger import get_logger

logger = get_logger("test_pipeline")


def test_imports():
    """Test that all modules can be imported."""
    logger.info("Testing module imports...")
    
    try:
        from app.speech.stt import transcribe_from_url
        logger.info("✓ STT module imported")
        
        from app.llm.responder import generate_response
        logger.info("✓ LLM responder imported")
        
        from app.speech.tts import text_to_speech_bytes
        logger.info("✓ TTS module imported")
        
        from app.rag.ingest import ingest_documents
        logger.info("✓ RAG ingest imported")
        
        from app.rag.vector_store import VectorStore
        logger.info("✓ Vector store imported")
        
        from app.rag.retrieve import retrieve_relevant_chunks
        logger.info("✓ RAG retrieve imported")
        
        from app.config.loader import load_org_config
        logger.info("✓ Config loader imported")
        
        return True
    except Exception as e:
        logger.exception(f"Import error: {e}")
        return False


def test_config_loader():
    """Test config loading."""
    logger.info("\nTesting config loader...")
    
    try:
        from app.config.loader import load_org_config
        
        config = load_org_config("sample_org")
        logger.info(f"✓ Loaded config: {config}")
        
        assert config["org_name"] == "Sample University"
        assert config["assistant_role"] == "Admission Helpdesk"
        logger.info("✓ Config values correct")
        
        return True
    except Exception as e:
        logger.exception(f"Config test error: {e}")
        return False


def test_document_ingestion():
    """Test document ingestion (chunking only, no embeddings)."""
    logger.info("\nTesting document ingestion...")
    
    try:
        from app.rag.ingest import extract_text_from_file, chunk_text
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        doc_path = os.path.join(base_dir, "data", "sample_org", "knowledge", "sample_faq.txt")
        
        # Extract text
        text = extract_text_from_file(doc_path)
        logger.info(f"✓ Extracted {len(text)} characters")
        
        # Chunk text
        chunks = chunk_text(text, chunk_size=500)
        logger.info(f"✓ Created {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks[:2]):
            logger.info(f"  Chunk {i+1} preview: {chunk[:100]}...")
        
        return True
    except Exception as e:
        logger.exception(f"Ingestion test error: {e}")
        return False


def test_vector_store():
    """Test vector store creation and search (without real embeddings)."""
    logger.info("\nTesting vector store...")
    
    try:
        from app.rag.vector_store import VectorStore
        import numpy as np
        
        # Create mock embeddings
        vector_store = VectorStore(dimension=1536)
        
        mock_chunks = [
            "What are your operating hours?",
            "How can I contact support?",
            "What services do you offer?"
        ]
        
        mock_embeddings = [
            np.random.rand(1536).tolist(),
            np.random.rand(1536).tolist(),
            np.random.rand(1536).tolist()
        ]
        
        mock_metadata = [
            {"source": "test.txt", "chunk_index": i} for i in range(3)
        ]
        
        vector_store.add_documents(mock_chunks, mock_embeddings, mock_metadata)
        logger.info(f"✓ Added {len(mock_chunks)} documents to vector store")
        
        # Test search
        query_embedding = np.random.rand(1536).tolist()
        results = vector_store.search(query_embedding, k=2)
        logger.info(f"✓ Search returned {len(results)} results")
        
        return True
    except Exception as e:
        logger.exception(f"Vector store test error: {e}")
        return False


def test_call_flow_structure():
    """Test that call flow structure is correct."""
    logger.info("\nTesting call flow structure...")
    
    try:
        from app.calls.inbound import router
        
        routes = [route.path for route in router.routes]
        logger.info(f"✓ Found routes: {routes}")
        
        assert "/voice/inbound" in routes
        assert "/voice/recording-callback" in routes
        logger.info("✓ All required routes present")
        
        return True
    except Exception as e:
        logger.exception(f"Call flow test error: {e}")
        return False


def main():
    logger.info("=" * 60)
    logger.info("AI Voice Calling Agent - Pipeline Test")
    logger.info("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Config Loader", test_config_loader),
        ("Document Ingestion", test_document_ingestion),
        ("Vector Store", test_vector_store),
        ("Call Flow Structure", test_call_flow_structure)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            failed += 1
            logger.error(f"✗ {test_name} FAILED with exception: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"Test Results: {passed} passed, {failed} failed")
    logger.info("=" * 60)
    
    if failed == 0:
        logger.info("✅ All tests passed!")
        logger.info("\nNext steps:")
        logger.info("1. Set OPENAI_API_KEY in .env file")
        logger.info("2. Run: python scripts/ingest_documents.py --org sample_org")
        logger.info("3. Start server: uvicorn app.main:app --reload")
        logger.info("4. Expose with ngrok: ngrok http 8000")
        logger.info("5. Configure Twilio webhook")
        return 0
    else:
        logger.error("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
