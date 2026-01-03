# AI Voice Calling Agent

An AI-powered voice calling agent that supports inbound and outbound calls
for organizations using document-based knowledge.

## Tech Stack
- **FastAPI** - Web framework
- **Twilio** - Voice calling infrastructure
- **OpenAI Whisper** - Speech-to-text
- **OpenAI GPT-4** - Language model
- **FAISS** - Vector similarity search
- **Amazon Polly** - Text-to-speech (optional)
- **PyPDF2** - PDF text extraction

## Features

### ✅ Complete Voice Pipeline
```
Inbound Call → Speech-to-Text → RAG Retrieval → LLM Response → Text-to-Speech → Caller
```

### ✅ RAG-Based Responses
- Extract text from PDFs and TXT files
- Chunk documents intelligently
- Create embeddings with OpenAI
- Store in FAISS vector database
- Retrieve relevant context for each query
- Ground LLM responses in your documents

### ✅ Multi-Tenant Architecture
- Organization-specific configurations
- Separate knowledge bases per org
- Dynamic config loading
- Phone number to org mapping (ready)

## Quick Start

### 1. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add:
# - OPENAI_API_KEY (required for STT, LLM, embeddings)
# - AWS credentials (optional, for Polly TTS)
# - Twilio credentials (for production)
```

### 3. Add Your Documents

```bash
# Add .txt or .pdf files to knowledge folder
cp your-docs.pdf data/sample_org/knowledge/
```

### 4. Ingest Documents

```bash
python scripts/ingest_documents.py --org sample_org
```

This will:
- Extract text from all documents
- Chunk into manageable pieces
- Create embeddings
- Build FAISS vector store

### 5. Test the Pipeline

```bash
python scripts/test_pipeline.py
```

Should show: ✅ All tests passed!

### 6. Start the Server

```bash
uvicorn app.main:app --reload
```

### 7. Expose with Ngrok (for Twilio)

```bash
ngrok http 8000
```

### 8. Configure Twilio

Set your Twilio voice webhook to:
```
https://<your-ngrok-url>/voice/inbound
```

## Outbound Calling

### Use Cases
- **Reminders**: Appointment reminders, payment due dates
- **Awareness**: Announcements, updates, policy changes
- **Surveys**: Feedback collection, satisfaction polls

### Single Outbound Call

```python
import requests

response = requests.post("http://localhost:8000/voice/outbound", json={
    "to_number": "+15551234567",
    "org_name": "sample_org",
    "call_type": "reminder",
    "message": "Your appointment is tomorrow at 2 PM",
    "gather_response": False
})

print(response.json())
# {"status": "success", "call_sid": "CA...", ...}
```

### Bulk Outbound Calls

```python
response = requests.post("http://localhost:8000/voice/outbound/bulk", json={
    "to_numbers": ["+15551234567", "+15559876543"],
    "org_name": "sample_org",
    "call_type": "awareness",
    "message": "Important update about our services"
})

print(response.json())
# {"status": "completed", "successful": 2, "failed": 0, ...}
```

### Survey with Response Recording

```python
response = requests.post("http://localhost:8000/voice/outbound", json={
    "to_number": "+15551234567",
    "call_type": "survey",
    "message": "How satisfied are you with our services?",
    "gather_response": True  # Records user's spoken response
})
```

### Try Examples

```bash
# Interactive examples
python scripts/outbound_examples.py
```

### Configuration Required

Add to `.env`:
```bash
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
BASE_URL=https://your-server.com  # Or ngrok URL
```

## Project Structure

```
ai-voice-calling-agent/
├── app/
│   ├── main.py                    # FastAPI app
│   ├── calls/
│   │   ├── inbound.py            # ✅ Full pipeline: STT→RAG→LLM→TTS
│   │   └── outbound.py           # Placeholder
│   ├── speech/
│   │   ├── stt.py                # ✅ OpenAI Whisper
│   │   └── tts.py                # ✅ Amazon Polly
│   ├── llm/
│   │   └── responder.py          # ✅ GPT-4 with RAG context
│   ├── rag/
│   │   ├── ingest.py             # ✅ Document processing
│   │   ├── vector_store.py       # ✅ FAISS wrapper
│   │   └── retrieve.py           # ✅ Semantic search
│   ├── config/
│   │   └── loader.py             # ✅ Multi-tenant config
│   └── utils/
│       └── logger.py             # Logging helper
├── data/
│   └── sample_org/
│       ├── config.json           # Org configuration
│       ├── knowledge/            # Your documents (.txt, .pdf)
│       └── vector_store/         # Generated FAISS index
├── scripts/
│   ├── ingest_documents.py       # CLI for document ingestion
│   └── test_pipeline.py          # Integration tests
└── requirements.txt
```

## How It Works

### Call Flow

1. **User calls your Twilio number**
2. **Twilio hits `/voice/inbound`**
   - Returns TwiML with "Please speak after the beep"
   - Starts recording
3. **User speaks their question**
4. **Twilio posts recording to `/voice/recording-callback`**
   - Downloads audio file
   - Transcribes with Whisper
5. **RAG Retrieval**
   - Converts question to embedding
   - Searches FAISS for top-3 relevant chunks
6. **LLM Generation**
   - Sends question + context to GPT-4
   - Gets grounded response
7. **Response to Caller**
   - Returns TwiML with `<Say>` (Twilio TTS)
   - Or use Polly for higher quality

### RAG Pipeline

```python
# Ingestion (one-time)
docs → extract_text → chunk → embeddings → FAISS

# Query (per call)
question → embedding → FAISS.search() → top_k_chunks → LLM context
```

## Configuration

### Organization Config (`data/{org}/config.json`)

```json
{
  "org_name": "Sample University",
  "assistant_role": "Admission Helpdesk",
  "language": "English",
  "tone": "polite",
  "knowledge_path": "data/sample_org/knowledge/"
}
```

### Adding New Organizations

```bash
# 1. Create org structure
mkdir -p data/my_org/knowledge
cp data/sample_org/config.json data/my_org/config.json

# 2. Edit config
vim data/my_org/config.json

# 3. Add documents
cp docs/*.pdf data/my_org/knowledge/

# 4. Ingest
python scripts/ingest_documents.py --org my_org
```

## Current Status

### ✅ Implemented (Days 1-7)
- [x] FastAPI server with health check
- [x] Twilio inbound call handling
- [x] Speech-to-text (Whisper)
- [x] LLM response generation (GPT-4)
- [x] Text-to-speech (Polly)
- [x] Document ingestion (PDF + TXT)
- [x] Vector store (FAISS)
- [x] RAG retrieval
- [x] Multi-tenant configuration
- [x] Complete voice pipeline
- [x] **Outbound calling (Reminder, Awareness, Survey)**
- [x] **Bulk outbound calls**

### 🚧 Coming Soon
- [ ] Conversation state management
- [ ] Call analytics dashboard
- [ ] Advanced phone routing

## Troubleshooting

### "No module named 'app'"
```bash
cd ai-voice-calling-agent
PYTHONPATH=$PWD uvicorn app.main:app --reload
```

### "No embeddings to add"
Make sure `OPENAI_API_KEY` is set in your `.env` file.

### "Vector store is empty"
Run `python scripts/ingest_documents.py --org sample_org` first.

### Twilio webhook errors
- Check ngrok is running: `ngrok http 8000`
- Verify webhook URL in Twilio console
- Check server logs for errors

## Cost Optimization

- **Whisper API**: ~$0.006 per minute of audio
- **GPT-4**: ~$0.03 per 1K tokens
- **Embeddings**: ~$0.0001 per 1K tokens
- **Polly**: 1M characters free/month
- **Twilio**: ~$0.01 per minute

**Typical call cost**: $0.05-0.15 per call

## Contributing

This is a reference implementation. Follow the patterns:
- One file = one responsibility
- Use type hints
- Log important events
- Handle errors gracefully
- Write docstrings

Use GitHub Copilot to accelerate development!
