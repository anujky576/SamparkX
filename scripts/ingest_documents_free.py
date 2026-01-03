#!/usr/bin/env python3
"""
FREE Document Ingestion Script
Uses local models instead of OpenAI
- Ollama for LLM (FREE)
- sentence-transformers for embeddings (FREE)
"""

import argparse
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.ingest_local import ingest_documents_local
from app.rag.vector_store import VectorStore
from app.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Ingest documents using FREE local models")
    parser.add_argument(
        "--org",
        type=str,
        default="sample_org",
        help="Organization name (default: sample_org)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="all-MiniLM-L6-v2",
        help="Embedding model (default: all-MiniLM-L6-v2, 384 dims)"
    )
    parser.add_argument(
        "--docs-path",
        type=str,
        help="Custom path to documents folder"
    )
    
    args = parser.parse_args()
    
    # Determine paths
    if args.docs_path:
        docs_path = Path(args.docs_path)
    else:
        docs_path = Path(f"data/{args.org}/knowledge")
    
    vector_store_path = Path(f"data/{args.org}/vector_store_local")
    
    # Check if documents folder exists
    if not docs_path.exists():
        logger.error(f"Documents folder not found: {docs_path}")
        print(f"❌ Documents folder not found: {docs_path}")
        print(f"\nCreate it with: mkdir -p {docs_path}")
        return 1
    
    logger.info(f"Ingesting documents for organization: {args.org}")
    logger.info(f"Documents path: {docs_path.absolute()}")
    logger.info(f"Vector store path: {vector_store_path.absolute()}")
    logger.info(f"Embedding model: {args.model}")
    
    print(f"\n🚀 FREE Document Ingestion (Local Models)")
    print(f"{'=' * 60}")
    print(f"Organization: {args.org}")
    print(f"Documents: {docs_path}")
    print(f"Model: {args.model} (FREE!)")
    print(f"{'=' * 60}\n")
    
    # Ingest documents
    logger.info("Starting ingestion...")
    print("📚 Processing documents...")
    
    result = ingest_documents_local(str(docs_path), model_name=args.model)
    
    chunks = result["chunks"]
    embeddings = result["embeddings"]
    metadata = result["metadata"]
    
    logger.info(f"Ingested {len(chunks)} chunks")
    print(f"✓ Extracted {len(chunks)} text chunks")
    
    if not embeddings:
        print("❌ Failed to create embeddings")
        print("\nMake sure sentence-transformers is installed:")
        print("  pip install sentence-transformers")
        return 1
    
    print(f"✓ Created {len(embeddings)} embeddings (dimension: {len(embeddings[0])})")
    
    # Build vector store
    logger.info("Building vector store...")
    print("\n🔧 Building vector store...")
    
    vector_store = VectorStore(dimension=len(embeddings[0]))
    vector_store.add_documents(
        embeddings=embeddings,
        chunks=chunks,
        metadata=metadata
    )
    
    print(f"✓ Added {len(chunks)} documents to vector store")
    
    # Save to disk
    vector_store_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Saving vector store to {vector_store_path}")
    print(f"\n💾 Saving to: {vector_store_path}")
    
    vector_store.save(str(vector_store_path))
    
    print(f"✓ Vector store saved")
    
    # Summary
    print(f"\n{'=' * 60}")
    print(f"✅ Ingestion complete! (100% FREE)")
    print(f"{'=' * 60}")
    print(f"Total chunks: {len(chunks)}")
    print(f"Embedding dimension: {len(embeddings[0])}")
    print(f"Vector store saved to: {vector_store_path}")
    print(f"\nNote: Using local embeddings (384-dim) instead of OpenAI (1536-dim)")
    print(f"This is FREE but may have slightly lower accuracy.")
    print(f"\n💡 Next steps:")
    print(f"  1. Test: python scripts/test_free_pipeline.py")
    print(f"  2. Start server: uvicorn app.main:app --reload")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
