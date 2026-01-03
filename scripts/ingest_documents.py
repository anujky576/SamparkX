#!/usr/bin/env python3
"""CLI tool to ingest documents and build vector store for an organization."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
from app.rag.ingest import ingest_documents
from app.rag.vector_store import VectorStore
from app.utils.logger import get_logger

logger = get_logger("ingest_cli")


def main():
    parser = argparse.ArgumentParser(
        description="Ingest documents and build vector store for an organization"
    )
    parser.add_argument(
        "--org",
        type=str,
        default="sample_org",
        help="Organization name (default: sample_org)"
    )
    parser.add_argument(
        "--docs-path",
        type=str,
        help="Path to documents directory (default: data/{org}/knowledge)"
    )
    
    args = parser.parse_args()
    
    # Build paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_path = args.docs_path or os.path.join(base_dir, "data", args.org, "knowledge")
    store_path = os.path.join(base_dir, "data", args.org, "vector_store")
    
    logger.info(f"Ingesting documents for organization: {args.org}")
    logger.info(f"Documents path: {docs_path}")
    logger.info(f"Vector store path: {store_path}")
    
    # Check if docs path exists
    if not os.path.exists(docs_path):
        logger.error(f"Documents path does not exist: {docs_path}")
        logger.info("Please add .txt or .pdf files to the knowledge directory")
        return 1
    
    # Ingest documents
    logger.info("Starting ingestion...")
    result = ingest_documents(docs_path)
    
    if not result["chunks"]:
        logger.warning("No documents were ingested")
        return 1
    
    logger.info(f"Ingested {len(result['chunks'])} chunks")
    
    # Create vector store
    logger.info("Building vector store...")
    vector_store = VectorStore()
    vector_store.add_documents(
        chunks=result["chunks"],
        embeddings=result["embeddings"],
        metadata=result["metadata"]
    )
    
    # Save vector store
    logger.info(f"Saving vector store to {store_path}")
    vector_store.save(store_path)
    
    logger.info("✅ Ingestion complete!")
    logger.info(f"Total chunks: {len(result['chunks'])}")
    logger.info(f"Vector store saved to: {store_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
