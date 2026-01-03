"""Vector store wrapper using FAISS for similarity search."""

import os
import pickle
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np
from app.utils.logger import get_logger

try:
    import faiss
except ImportError:
    faiss = None

logger = get_logger("vector_store")


class VectorStore:
    """FAISS-based vector store for document chunks."""
    
    def __init__(self, dimension: int = 1536):
        """Initialize vector store.
        
        Args:
            dimension: Embedding dimension (1536 for OpenAI ada-002)
        """
        if faiss is None:
            raise ImportError("faiss-cpu not installed")
        
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.chunks: List[str] = []
        self.metadata: List[Dict] = []
    
    def add_documents(self, chunks: List[str], embeddings: List[List[float]], metadata: List[Dict]):
        """Add documents to the vector store.
        
        Args:
            chunks: Text chunks
            embeddings: Embedding vectors
            metadata: Metadata for each chunk
        """
        if not embeddings:
            logger.warning("No embeddings to add")
            return
        
        # Convert to numpy array
        embeddings_np = np.array(embeddings).astype('float32')
        
        # Add to FAISS index
        self.index.add(embeddings_np)
        
        # Store chunks and metadata
        self.chunks.extend(chunks)
        self.metadata.extend(metadata)
        
        logger.info(f"Added {len(chunks)} documents. Total: {len(self.chunks)}")
    
    def search(self, query_embedding: List[float], k: int = 5) -> List[Tuple[str, Dict, float]]:
        """Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
        
        Returns:
            List of (chunk, metadata, distance) tuples
        """
        if len(self.chunks) == 0:
            logger.warning("Vector store is empty")
            return []
        
        # Convert query to numpy array
        query_np = np.array([query_embedding]).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_np, min(k, len(self.chunks)))
        
        # Prepare results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.chunks):
                results.append((
                    self.chunks[idx],
                    self.metadata[idx],
                    float(dist)
                ))
        
        logger.info(f"Found {len(results)} similar documents")
        return results
    
    def save(self, path: str):
        """Save vector store to disk.
        
        Args:
            path: Directory to save to
        """
        os.makedirs(path, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, os.path.join(path, "index.faiss"))
        
        # Save chunks and metadata
        with open(os.path.join(path, "data.pkl"), 'wb') as f:
            pickle.dump({
                'chunks': self.chunks,
                'metadata': self.metadata
            }, f)
        
        logger.info(f"Saved vector store to {path}")
    
    def load(self, path: str):
        """Load vector store from disk.
        
        Args:
            path: Directory to load from
        """
        index_path = os.path.join(path, "index.faiss")
        data_path = os.path.join(path, "data.pkl")
        
        if not os.path.exists(index_path) or not os.path.exists(data_path):
            logger.warning(f"Vector store not found at {path}")
            return
        
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        
        # Load chunks and metadata
        with open(data_path, 'rb') as f:
            data = pickle.load(f)
            self.chunks = data['chunks']
            self.metadata = data['metadata']
        
        logger.info(f"Loaded vector store from {path}: {len(self.chunks)} chunks")
