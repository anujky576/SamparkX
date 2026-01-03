"""
Free Document Ingestion using Local Models
Alternative to OpenAI embeddings
"""

import os
import logging
from typing import List, Dict
from pathlib import Path

from app.rag.ingest import extract_text_from_file, chunk_text
from app.rag.local_embeddings import create_local_embeddings

logger = logging.getLogger(__name__)


def ingest_documents_local(docs_path: str, model_name: str = "all-MiniLM-L6-v2") -> Dict:
    """
    Ingest documents using FREE local embeddings
    
    Args:
        docs_path: Path to documents folder
        model_name: Local embedding model name
        
    Returns:
        Dictionary with chunks, embeddings, and metadata
    """
    logger.info(f"Ingesting documents from {docs_path} (using local embeddings)")
    
    # Get all text and PDF files
    path = Path(docs_path)
    files = list(path.glob("*.txt")) + list(path.glob("*.pdf"))
    
    logger.info(f"Found {len(files)} files")
    
    all_chunks = []
    all_metadata = []
    
    # Process each file
    for file_path in files:
        try:
            logger.info(f"Processing {file_path.name}")
            
            # Extract text
            text = extract_text_from_file(str(file_path))
            
            # Chunk text
            chunks = chunk_text(text, chunk_size=500, overlap=50)
            logger.info(f"Created {len(chunks)} chunks from {file_path.name}")
            
            # Add to collection
            all_chunks.extend(chunks)
            
            # Create metadata
            for i, chunk in enumerate(chunks):
                all_metadata.append({
                    "source": str(file_path),
                    "chunk_id": i,
                    "filename": file_path.name
                })
                
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
    
    # Create embeddings with local model
    logger.info(f"Creating local embeddings for {len(all_chunks)} chunks...")
    embeddings = create_local_embeddings(all_chunks, model_name)
    
    if not embeddings:
        logger.error("Failed to create local embeddings")
        return {
            "chunks": all_chunks,
            "embeddings": [],
            "metadata": all_metadata
        }
    
    logger.info(f"Ingestion complete: {len(all_chunks)} chunks, {len(embeddings)} embeddings")
    
    return {
        "chunks": all_chunks,
        "embeddings": embeddings,
        "metadata": all_metadata
    }


if __name__ == "__main__":
    # Test local ingestion
    import sys
    
    if len(sys.argv) > 1:
        docs_path = sys.argv[1]
    else:
        docs_path = "data/sample_org/knowledge"
    
    print(f"Testing local document ingestion from: {docs_path}")
    
    result = ingest_documents_local(docs_path)
    
    print(f"\n✓ Processed {len(result['chunks'])} chunks")
    print(f"✓ Created {len(result['embeddings'])} embeddings")
    
    if result['embeddings']:
        print(f"✓ Embedding dimension: {len(result['embeddings'][0])}")
        print(f"✓ First chunk: {result['chunks'][0][:100]}...")
