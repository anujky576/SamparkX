# Usage Guide - AI Voice Calling Agent

## Table of Contents
1. [Getting Started](#getting-started)
2. [Document Management](#document-management)
3. [Testing Locally](#testing-locally)
4. [Production Deployment](#production-deployment)
5. [Multi-Tenant Setup](#multi-tenant-setup)
6. [API Reference](#api-reference)

---

## Getting Started

### Prerequisites
- Python 3.10 or higher
- OpenAI API key
- Twilio account (for production calls)
- AWS account (optional, for Polly TTS)
- ngrok (for local testing with Twilio)

### Installation

```bash
# Clone and navigate to project
cd ai-voice-calling-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

Create `.env` file in project root:

```bash
# Required for STT, LLM, and embeddings
OPENAI_API_KEY=sk-...

# Optional: For Amazon Polly TTS (higher quality)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# Optional: Twilio credentials
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

---

## Document Management

### Adding Documents

1. **Supported Formats**: `.txt` and `.pdf`

2. **Add files to knowledge folder**:
```bash
cp your-faq.pdf data/sample_org/knowledge/
cp policies.txt data/sample_org/knowledge/
```

3. **Ingest documents** (creates vector store):
```bash
python scripts/ingest_documents.py --org sample_org
```

Expected output:
```
INFO: Found 2 files
INFO: Processing your-faq.pdf
INFO: Created 15 chunks from your-faq.pdf
INFO: Processing policies.txt
INFO: Created 8 chunks from policies.txt
INFO: Created 23 embeddings
INFO: ✅ Ingestion complete!
```

### Document Best Practices

**Good Document Structure**:
```markdown
# Organization FAQ

## Admission Questions

### How do I apply?
Complete the online application at...

### What are the deadlines?
- Fall semester: May 1st
- Spring semester: November 1st
```

**Tips**:
- Use clear headings and sections
- Keep answers concise (1-3 paragraphs)
- Include specific details (dates, prices, requirements)
- Avoid long narrative prose
- Update regularly and re-ingest

### Updating Documents

When you modify or add documents:

```bash
# Re-run ingestion
python scripts/ingest_documents.py --org sample_org

# Restart server to load new vector store
pkill -f "uvicorn app.main"
uvicorn app.main:app --reload
```

---

## Testing Locally

### 1. Run Tests

```bash
# Test all components
python scripts/test_pipeline.py
```

Should output:
```
✅ All tests passed!
```

### 2. Start Server

```bash
# With auto-reload for development
uvicorn app.main:app --reload --port 8000

# Or specify PYTHONPATH if needed
PYTHONPATH=$PWD uvicorn app.main:app --reload
```

### 3. Test Endpoints

**Health Check**:
```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

**Inbound Call Simulation**:
```bash
curl -X POST http://localhost:8000/voice/inbound
# Returns TwiML with <Record> verb
```

**Recording Callback (with mock data)**:
```bash
curl -X POST http://localhost:8000/voice/recording-callback \
  -d "RecordingUrl=https://example.com/test.wav" \
  -d "CallSid=test-call-123"
# Returns TwiML with AI response
```

### 4. Test with Twilio (Real Calls)

**Setup ngrok**:
```bash
ngrok http 8000
# Note the HTTPS URL: https://abc123.ngrok.io
```

**Configure Twilio**:
1. Go to Twilio Console
2. Phone Numbers → Your number
3. Voice & Fax → Webhook
4. Set to: `https://abc123.ngrok.io/voice/inbound`
5. Method: POST
6. Save

**Make a test call**:
- Call your Twilio number
- Wait for prompt: "Please speak your question after the beep"
- Ask: "What are your operating hours?"
- Listen to AI response

**Check Logs**:
```bash
# Server logs show:
INFO: Recording callback for call CAxxxxx
INFO: User said: What are your operating hours
INFO: Retrieving relevant chunks for: What are your operating hours
INFO: Retrieved 3 relevant chunks
INFO: Generating response for: What are your operating hours
INFO: Generated response: We are open Monday through Friday...
```

---

## Production Deployment

### Option 1: Cloud VM (AWS EC2, GCP, etc.)

```bash
# 1. SSH to server
ssh user@your-server.com

# 2. Clone and setup
git clone your-repo
cd ai-voice-calling-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
vim .env  # Add your keys

# 4. Ingest documents
python scripts/ingest_documents.py --org sample_org

# 5. Run with gunicorn (production server)
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Option 2: Docker

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ingest documents at build time (or mount volume)
RUN python scripts/ingest_documents.py --org sample_org

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t voice-agent .
docker run -p 8000:8000 --env-file .env voice-agent
```

### Option 3: Platform as a Service (Heroku, Railway, etc.)

```yaml
# railway.toml or similar
[build]
  builder = "python"

[deploy]
  startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

### SSL/HTTPS

Twilio requires HTTPS. Options:
- **nginx** with Let's Encrypt
- **Caddy** (auto HTTPS)
- **Cloud load balancer**
- **ngrok** (dev only)

---

## Multi-Tenant Setup

### Creating a New Organization

**1. Create directory structure**:
```bash
mkdir -p data/university_x/knowledge
mkdir -p data/university_x/vector_store
```

**2. Copy and edit config**:
```bash
cp data/sample_org/config.json data/university_x/config.json
```

Edit `data/university_x/config.json`:
```json
{
  "org_name": "University X",
  "assistant_role": "Student Services Assistant",
  "language": "English",
  "tone": "friendly",
  "knowledge_path": "data/university_x/knowledge/"
}
```

**3. Add documents**:
```bash
cp university_x_docs/*.pdf data/university_x/knowledge/
```

**4. Ingest**:
```bash
python scripts/ingest_documents.py --org university_x
```

**5. Map phone number** (edit `app/config/loader.py`):
```python
def get_org_from_phone(phone_number: str) -> str:
    """Map phone number to organization."""
    mapping = {
        "+15551234567": "sample_org",
        "+15559876543": "university_x",
    }
    return mapping.get(phone_number, "sample_org")
```

**6. Update inbound handler** (edit `app/calls/inbound.py`):
```python
from app.config.loader import get_org_from_phone

@router.post("/voice/inbound")
async def inbound_call(request: Request, To: str = Form(None)):
    org_name = get_org_from_phone(To)
    # Use org_name for config and RAG retrieval
```

---

## API Reference

### Endpoints

#### `GET /health`
Health check endpoint.

**Response**:
```json
{"status": "ok"}
```

#### `POST /voice/inbound`
Twilio webhook for incoming calls.

**Expected Form Data** (from Twilio):
- `From`: Caller's phone number
- `To`: Your Twilio number
- `CallSid`: Unique call identifier

**Response**: TwiML XML
```xml
<Response>
  <Say>Hello. Please speak your question after the beep.</Say>
  <Record action="/voice/recording-callback" maxLength="30" method="POST"/>
</Response>
```

#### `POST /voice/recording-callback`
Handles recorded audio from Twilio.

**Form Data**:
- `RecordingUrl`: URL to audio file
- `CallSid`: Call identifier

**Response**: TwiML with AI response
```xml
<Response>
  <Say>We are open Monday through Friday from 9 AM to 5 PM.</Say>
</Response>
```

**Processing Steps**:
1. Download audio from RecordingUrl
2. Transcribe with Whisper
3. Retrieve relevant context from vector store
4. Generate response with GPT-4
5. Return TwiML

---

## Advanced Configuration

### Customizing LLM Behavior

Edit `app/llm/responder.py`:

```python
# Change model
response = client.chat.completions.create(
    model="gpt-4",  # or "gpt-3.5-turbo" for lower cost
    ...
)

# Adjust temperature (0 = deterministic, 1 = creative)
temperature=0.7,

# Increase/decrease response length
max_tokens=150,
```

### Customizing RAG

Edit `app/rag/retrieve.py`:

```python
# Change number of context chunks
context_chunks = retrieve_relevant_chunks(query, k=5)  # default: 3

# Edit chunking strategy in ingest.py
chunks = chunk_text(text, chunk_size=1000, overlap=100)
```

### Using Polly TTS (Higher Quality)

Uncomment in `app/calls/inbound.py`:

```python
from app.speech.tts import text_to_speech_bytes

audio_bytes = text_to_speech_bytes(ai_response)
# Save to file server or S3
audio_url = upload_audio(audio_bytes)

vr = VoiceResponse()
vr.play(audio_url)  # Instead of Say
```

---

## Monitoring and Debugging

### View Server Logs

```bash
tail -f server.log
```

### Common Log Messages

```
INFO inbound: Responding to inbound call
INFO stt: Downloading audio from https://...
INFO stt: Transcribing audio with Whisper...
INFO stt: Transcription: What are your hours
INFO rag_retrieve: Retrieving relevant chunks
INFO llm: Generating response for: What are your hours
INFO llm: Generated response: We are open...
```

### Debugging Tips

**No response from RAG**:
- Check vector store exists: `ls data/sample_org/vector_store/`
- Check chunks: `python -c "from app.rag.retrieve import get_vector_store; vs = get_vector_store(); print(len(vs.chunks))"`

**Transcription errors**:
- Verify OPENAI_API_KEY is set
- Check audio quality (Twilio recording)
- Test with clear speech

**LLM hallucinating**:
- Verify RAG retrieval returns relevant chunks
- Add more specific documents
- Lower temperature parameter

---

## Performance Tuning

### Response Time Optimization

Average latencies:
- STT (Whisper): 2-5s
- RAG retrieval: 0.1-0.5s
- LLM generation: 1-3s
- **Total**: 3-8s per response

**Optimization tips**:
- Use `gpt-3.5-turbo` instead of `gpt-4` (2x faster)
- Cache frequent queries
- Pre-generate responses for common questions
- Use streaming for LLM responses

### Cost Optimization

**Per-call breakdown**:
- Whisper: $0.006/min
- Embeddings: negligible
- GPT-4: $0.03 avg
- Twilio: $0.01/min

**Save money**:
- Use GPT-3.5-turbo ($0.002 vs $0.03)
- Limit max_tokens
- Cache LLM responses
- Use Twilio's built-in TTS (free) vs Polly

---

## Next Steps

1. **Test thoroughly** with real questions
2. **Add more documents** to improve coverage
3. **Monitor call quality** and iterate
4. **Collect feedback** from users
5. **Expand to outbound calls**
6. **Build admin dashboard**

For issues or questions, check the logs first, then review this guide.
