"""Retrieval utilities for RAG."""

import os
from typing import List, Tuple, Dict
from openai import OpenAI
from app.utils.logger import get_logger
from app.rag.vector_store import VectorStore

logger = get_logger("rag_retrieve")

# Global vector store instance
_vector_store = None


def get_vector_store(org_name: str = "sample_org") -> VectorStore:
    """Get or create vector store for an organization.
    
    Args:
        org_name: Organization name
    
    Returns:
        VectorStore instance
    """
    global _vector_store
    
    if _vector_store is None:
        _vector_store = VectorStore()
        
        # Try to load existing vector store
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        store_path = os.path.join(base_dir, "data", org_name, "vector_store")
        
        if os.path.exists(store_path):
            try:
                _vector_store.load(store_path)
                logger.info(f"Loaded vector store for {org_name}")
            except Exception as e:
                logger.warning(f"Could not load vector store: {e}")
    
    return _vector_store


def create_query_embedding(query: str) -> List[float]:
    """Create embedding for query text.
    
    Args:
        query: Query text
    
    Returns:
        Embedding vector
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=query
        )
        
        return response.data[0].embedding
    
    except Exception as e:
        logger.exception(f"Error creating query embedding: {e}")
        return []


def retrieve_relevant_chunks(query: str, k: int = 5, org_name: str = "sample_org") -> List[str]:
    """Return top-k relevant chunks for query.
    
    Args:
        query: User query
        k: Number of chunks to retrieve
        org_name: Organization name
    
    Returns:
        List of relevant text chunks
    """
    try:
        logger.info(f"Retrieving relevant chunks for: {query}")
        
        # Get vector store
        vector_store = get_vector_store(org_name)
        
        if len(vector_store.chunks) == 0:
            logger.warning("Vector store is empty. No documents ingested yet.")
            return []
        
        # Create query embedding
        query_embedding = create_query_embedding(query)
        if not query_embedding:
            return []
        
        # Search for similar chunks
        results = vector_store.search(query_embedding, k=k)
        
        # Extract just the text chunks
        chunks = [chunk for chunk, metadata, distance in results]
        
        logger.info(f"Retrieved {len(chunks)} relevant chunks")
        return chunks
    
    except Exception as e:
        logger.exception(f"Error retrieving chunks: {e}")
        return []
