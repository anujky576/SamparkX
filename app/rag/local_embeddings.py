"""
Local Embeddings using sentence-transformers (FREE!)
Alternative to OpenAI Embeddings
"""

import logging
import numpy as np
from typing import List, Union

logger = logging.getLogger(__name__)

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not installed. Install with: pip install sentence-transformers")


class LocalEmbedder:
    """Free local embeddings using sentence-transformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize local embedder
        
        Args:
            model_name: HuggingFace model (default: all-MiniLM-L6-v2, 384 dims)
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers required. Install: pip install sentence-transformers")
        
        logger.info(f"Loading local embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.dimension}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Create embedding for single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist()


def create_local_embeddings(texts: Union[str, List[str]], model_name: str = "all-MiniLM-L6-v2") -> List[List[float]]:
    """
    Create embeddings using local model (100% FREE)
    
    Args:
        texts: Single text or list of texts
        model_name: Model to use
        
    Returns:
        List of embedding vectors
    """
    if not TRANSFORMERS_AVAILABLE:
        logger.error("sentence-transformers not installed")
        return []
    
    try:
        embedder = LocalEmbedder(model_name)
        
        if isinstance(texts, str):
            texts = [texts]
        
        logger.info(f"Creating {len(texts)} local embeddings...")
        embeddings = embedder.embed_batch(texts)
        logger.info(f"Created {len(embeddings)} embeddings (dimension: {len(embeddings[0])})")
        
        return embeddings
        
    except Exception as e:
        logger.error(f"Error creating local embeddings: {e}")
        return []


if __name__ == "__main__":
    # Test local embeddings
    print("Testing Local Embeddings...")
    
    if not TRANSFORMERS_AVAILABLE:
        print("✗ sentence-transformers not installed")
        print("Install with: pip install sentence-transformers")
    else:
        print("✓ sentence-transformers available")
        
        # Test embedding creation
        texts = [
            "What are your operating hours?",
            "How can I contact support?",
            "We are open Monday-Friday 9 AM to 5 PM."
        ]
        
        embeddings = create_local_embeddings(texts)
        
        if embeddings:
            print(f"✓ Created {len(embeddings)} embeddings")
            print(f"✓ Embedding dimension: {len(embeddings[0])}")
            print(f"✓ First embedding preview: {embeddings[0][:5]}...")
        else:
            print("✗ Failed to create embeddings")
