#!/bin/bash

# 🧪 Launch AI Voice Agent Testing Interface

echo "🧪 Starting AI Voice Agent Test Lab..."
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama not running. Starting it..."
    ollama serve > /dev/null 2>&1 &
    sleep 2
fi

# Check vector store
if [ ! -d "data/sample_org/vector_store_local" ]; then
    echo "⚠️  Vector store not found. Running ingestion..."
    python scripts/ingest_documents_free.py --org sample_org
fi

echo "✅ All systems ready!"
echo ""
echo "🌐 Opening testing interface..."
echo "   URL: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Launch Streamlit
streamlit run ui/test_interface.py --server.port 8501 --server.headless true
