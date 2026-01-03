"""Document ingestion utilities: read files, chunk, and create embeddings."""

import os
from pathlib import Path
from typing import List, Dict
from openai import OpenAI
from app.utils.logger import get_logger

logger = get_logger("rag_ingest")


def extract_text_from_file(file_path: str) -> str:
    """Extract text from a file (supports .txt and .pdf).
    
    Args:
        file_path: Path to the document
    
    Returns:
        Extracted text content
    """
    ext = Path(file_path).suffix.lower()
    
    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    elif ext == '.pdf':
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            logger.warning("PyPDF2 not installed. Install with: pip install PyPDF2")
            return ""
    
    else:
        logger.warning(f"Unsupported file type: {ext}")
        return ""


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum characters per chunk
        overlap: Overlap between chunks
    
    Returns:
        List of text chunks
    """
    chunks = []
    words = text.split()
    current_chunk = []
    current_length = 0
    
    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        
        if current_length >= chunk_size:
            chunks.append(" ".join(current_chunk))
            # Keep last few words for overlap
            overlap_words = int(overlap / (current_length / len(current_chunk)))
            current_chunk = current_chunk[-overlap_words:] if overlap_words > 0 else []
            current_length = sum(len(w) + 1 for w in current_chunk)
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks


def create_embeddings(texts: List[str]) -> List[List[float]]:
    """Create embeddings for text chunks using OpenAI.
    
    Args:
        texts: List of text chunks
    
    Returns:
        List of embedding vectors
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        embeddings = []
        for text in texts:
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            embeddings.append(response.data[0].embedding)
        
        logger.info(f"Created {len(embeddings)} embeddings")
        return embeddings
    
    except Exception as e:
        logger.exception(f"Error creating embeddings: {e}")
        return []


def ingest_documents(path: str) -> Dict:
    """Read documents from `path` and prepare them for vector storage.
    
    Args:
        path: Directory containing documents
    
    Returns:
        Dict with chunks and embeddings
    """
    logger.info(f"Ingesting documents from {path}")
    
    all_chunks = []
    all_metadata = []
    
    # Find all supported files
    path_obj = Path(path)
    if not path_obj.exists():
        logger.error(f"Path does not exist: {path}")
        return {"chunks": [], "embeddings": [], "metadata": []}
    
    files = list(path_obj.glob('*.txt')) + list(path_obj.glob('*.pdf'))
    logger.info(f"Found {len(files)} files")
    
    for file_path in files:
        logger.info(f"Processing {file_path.name}")
        
        # Extract text
        text = extract_text_from_file(str(file_path))
        if not text.strip():
            logger.warning(f"No text extracted from {file_path.name}")
            continue
        
        # Chunk text
        chunks = chunk_text(text)
        logger.info(f"Created {len(chunks)} chunks from {file_path.name}")
        
        # Store chunks with metadata
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadata.append({
                "source": file_path.name,
                "chunk_index": i
            })
    
    # Create embeddings
    embeddings = create_embeddings(all_chunks)
    
    logger.info(f"Ingestion complete: {len(all_chunks)} chunks, {len(embeddings)} embeddings")
    
    return {
        "chunks": all_chunks,
        "embeddings": embeddings,
        "metadata": all_metadata
    }
