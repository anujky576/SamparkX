#!/bin/bash
# Quick start script for AI Voice Calling Agent

set -e

echo "🚀 AI Voice Calling Agent - Quick Start"
echo "========================================"

# Check Python version
echo ""
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version found"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source .venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found. Creating from example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY"
    echo "   nano .env"
    echo ""
    read -p "Press Enter when you've added your API key..."
fi

# Check if OPENAI_API_KEY is set
source .env
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_key" ]; then
    echo ""
    echo "❌ OPENAI_API_KEY not configured in .env"
    echo "   Please edit .env and add your OpenAI API key"
    exit 1
fi

# Check if documents exist
doc_count=$(find data/sample_org/knowledge -name "*.txt" -o -name "*.pdf" 2>/dev/null | wc -l)
echo ""
echo "Checking for documents..."
echo "✓ Found $doc_count document(s) in data/sample_org/knowledge/"

if [ "$doc_count" -eq 0 ]; then
    echo "⚠️  No documents found. Add .txt or .pdf files to data/sample_org/knowledge/"
fi

# Check if vector store exists
if [ ! -d "data/sample_org/vector_store" ]; then
    echo ""
    echo "Running document ingestion..."
    PYTHONPATH=$PWD python scripts/ingest_documents.py --org sample_org
    echo "✓ Vector store created"
else
    echo "✓ Vector store already exists"
fi

# Run tests
echo ""
echo "Running tests..."
PYTHONPATH=$PWD python scripts/test_pipeline.py | tail -10

# Start server
echo ""
echo "========================================"
echo "✅ Setup complete!"
echo "========================================"
echo ""
echo "Starting server on http://localhost:8000"
echo ""
echo "Test endpoints:"
echo "  curl http://localhost:8000/health"
echo "  curl -X POST http://localhost:8000/voice/inbound"
echo ""
echo "For Twilio testing:"
echo "  1. In another terminal, run: ngrok http 8000"
echo "  2. Copy the HTTPS URL"
echo "  3. Configure Twilio webhook to: https://YOUR_NGROK_URL/voice/inbound"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start server
PYTHONPATH=$PWD uvicorn app.main:app --reload --port 8000
