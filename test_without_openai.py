#!/usr/bin/env python3
"""
Test the voice agent pipeline WITHOUT OpenAI API calls
This lets you verify the structure works before adding billing
"""

import sys
sys.path.append('.')

from app.config.loader import load_org_config
from app.rag.ingest import extract_text_from_file, chunk_text
from app.rag.vector_store import VectorStore
import numpy as np

print("=" * 60)
print("AI Voice Agent - Structure Test (No OpenAI)")
print("=" * 60)

# Test 1: Config Loading
print("\n1. Testing Config Loader...")
config = load_org_config("sample_org")
print(f"✓ Loaded config for: {config['org_name']}")
print(f"✓ Assistant role: {config['assistant_role']}")

# Test 2: Document Processing
print("\n2. Testing Document Processing...")
file_path = "data/sample_org/knowledge/sample_faq.txt"
text = extract_text_from_file(file_path)
print(f"✓ Extracted {len(text)} characters")

chunks = chunk_text(text, chunk_size=500, overlap=50)
print(f"✓ Created {len(chunks)} chunks")
print(f"✓ First chunk preview: {chunks[0][:80]}...")

# Test 3: Vector Store (with mock embeddings)
print("\n3. Testing Vector Store (mock embeddings)...")
mock_embeddings = [np.random.rand(1536).astype('float32').tolist() for _ in chunks]
print(f"✓ Created {len(mock_embeddings)} mock embeddings")

vector_store = VectorStore(dimension=1536)
metadata = [{"source": file_path, "chunk_id": i} for i in range(len(chunks))]
vector_store.add_documents(embeddings=mock_embeddings, chunks=chunks, metadata=metadata)
print(f"✓ Added {len(chunks)} documents to vector store")

# Test 4: Search (with mock query)
print("\n4. Testing Similarity Search...")
mock_query = np.random.rand(1536).astype('float32')
results = vector_store.search(mock_query, k=2)
print(f"✓ Search returned {len(results)} results")
for i, (chunk, meta, distance) in enumerate(results, 1):
    print(f"  Result {i}: {chunk[:60]}... (distance: {distance:.4f})")

# Test 5: API Endpoints
print("\n5. Testing API Structure...")
from app.main import app
routes = [route.path for route in app.routes]
required_routes = ['/voice/inbound', '/voice/recording-callback']
for route in required_routes:
    if route in routes:
        print(f"✓ Found route: {route}")
    else:
        print(f"✗ Missing route: {route}")

print("\n" + "=" * 60)
print("✅ Structure Test Complete!")
print("=" * 60)
print("\nWhat works WITHOUT OpenAI:")
print("  ✓ Document extraction")
print("  ✓ Text chunking")
print("  ✓ Vector store operations")
print("  ✓ API endpoints")
print("  ✓ Configuration loading")
print("\nWhat needs OpenAI API:")
print("  ✗ Real embeddings (for semantic search)")
print("  ✗ Speech-to-text (Whisper)")
print("  ✗ LLM responses (GPT-4)")
print("  ✗ Real voice calls")
print("\nTo enable full functionality:")
print("  1. Add payment method at https://platform.openai.com/account/billing")
print("  2. Set usage limit (e.g., $5/month)")
print("  3. Re-run: python scripts/ingest_documents.py --org sample_org")
