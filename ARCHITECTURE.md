# Architecture Overview

## System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI Voice Calling Agent                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────┐     ┌──────────────────────────────────────┐
│   Caller    │────▶│  Twilio Voice Infrastructure         │
│             │     │  - Phone routing                      │
│             │◀────│  - Voice recording                    │
└─────────────┘     │  - Built-in TTS (backup)             │
                    └───────────┬──────────────────────────┘
                                │ HTTPS Webhook
                                ▼
                    ┌───────────────────────────────────────┐
                    │     FastAPI Server (Port 8000)        │
                    │  ┌─────────────────────────────────┐  │
                    │  │  /voice/inbound                 │  │
                    │  │  - Returns TwiML <Record>       │  │
                    │  └─────────────────────────────────┘  │
                    │  ┌─────────────────────────────────┐  │
                    │  │  /voice/recording-callback      │  │
                    │  │  - Orchestrates full pipeline   │  │
                    │  └─────────────────────────────────┘  │
                    └───────────┬───────────────────────────┘
                                │
                                ▼
              ┌─────────────────────────────────────┐
              │     Speech-to-Text (STT)            │
              │  ┌──────────────────────────────┐   │
              │  │  OpenAI Whisper API          │   │
              │  │  - Downloads audio from URL  │   │
              │  │  - Transcribes to text       │   │
              │  └──────────────────────────────┘   │
              └─────────────┬───────────────────────┘
                            │ Transcribed Text
                            ▼
              ┌─────────────────────────────────────┐
              │     RAG Retrieval Layer             │
              │  ┌──────────────────────────────┐   │
              │  │  Query Embedding             │   │
              │  │  - OpenAI ada-002            │   │
              │  └──────────┬───────────────────┘   │
              │             ▼                        │
              │  ┌──────────────────────────────┐   │
              │  │  FAISS Vector Store          │   │
              │  │  - Similarity search         │   │
              │  │  - Returns top-K chunks      │   │
              │  └──────────┬───────────────────┘   │
              └─────────────┼───────────────────────┘
                            │ Relevant Context
                            ▼
              ┌─────────────────────────────────────┐
              │     LLM Response Generation         │
              │  ┌──────────────────────────────┐   │
              │  │  OpenAI GPT-4                │   │
              │  │  - User query                │   │
              │  │  - Retrieved context         │   │
              │  │  - Organization config       │   │
              │  │  → Grounded response         │   │
              │  └──────────┬───────────────────┘   │
              └─────────────┼───────────────────────┘
                            │ AI Response Text
                            ▼
              ┌─────────────────────────────────────┐
              │     Text-to-Speech (TTS)            │
              │  ┌──────────────────────────────┐   │
              │  │  Option 1: Twilio <Say>      │   │
              │  │  - Built-in, simple          │   │
              │  └──────────────────────────────┘   │
              │  ┌──────────────────────────────┐   │
              │  │  Option 2: Amazon Polly      │   │
              │  │  - Neural voices, HD quality │   │
              │  └──────────────────────────────┘   │
              └─────────────┬───────────────────────┘
                            │ TwiML Response
                            ▼
                    ┌───────────────────────────────┐
                    │  Twilio returns audio to      │
                    │  caller                       │
                    └───────────────────────────────┘
```

## Data Flow

### 1. Document Ingestion (One-time Setup)

```
Documents (.txt, .pdf)
    │
    ▼
┌──────────────────┐
│  Extract Text    │  PyPDF2 / file reading
└────────┬─────────┘
         ▼
┌──────────────────┐
│  Chunk Text      │  500 chars, 50 overlap
└────────┬─────────┘
         ▼
┌──────────────────┐
│  Create          │  OpenAI ada-002
│  Embeddings      │  1536 dimensions
└────────┬─────────┘
         ▼
┌──────────────────┐
│  Store in FAISS  │  IndexFlatL2
│  + Save to Disk  │  index.faiss + data.pkl
└──────────────────┘
```

### 2. Call Processing (Runtime)

```
User Speech
    │
    ▼
[Whisper STT] → "What are your hours?"
    │
    ▼
[Create Embedding] → [1536-dim vector]
    │
    ▼
[FAISS Search] → Top-3 relevant chunks
    │           "We are open Monday-Friday..."
    ▼
[GPT-4] ← User query + Retrieved context
    │
    ▼
AI Response: "We are open Monday through Friday from 9 AM to 5 PM EST."
    │
    ▼
[Twilio TTS] → Spoken to caller
```

## File Organization

```
ai-voice-calling-agent/
│
├── app/                          # Main application
│   ├── main.py                  # FastAPI entry point
│   │
│   ├── calls/                   # Call handling
│   │   ├── inbound.py          # Webhook endpoints
│   │   └── outbound.py         # Future: outbound calls
│   │
│   ├── speech/                  # Audio processing
│   │   ├── stt.py              # Whisper integration
│   │   └── tts.py              # Polly integration
│   │
│   ├── llm/                     # Language model
│   │   └── responder.py        # GPT-4 + context
│   │
│   ├── rag/                     # Knowledge retrieval
│   │   ├── ingest.py           # Document processing
│   │   ├── vector_store.py     # FAISS wrapper
│   │   └── retrieve.py         # Query handling
│   │
│   ├── config/                  # Configuration
│   │   └── loader.py           # Org configs
│   │
│   └── utils/                   # Utilities
│       └── logger.py           # Logging
│
├── data/                         # Org-specific data
│   └── {org_name}/
│       ├── config.json          # Org settings
│       ├── knowledge/           # Documents
│       └── vector_store/        # Generated FAISS
│
├── scripts/                      # CLI tools
│   ├── ingest_documents.py     # Build vector store
│   └── test_pipeline.py        # Integration tests
│
└── docs/
    ├── README.md               # Quick start
    ├── USAGE.md               # Detailed guide
    ├── CHANGELOG.md           # Development log
    └── ARCHITECTURE.md        # This file
```

## Technology Choices

### Why FastAPI?
- Fast, modern Python web framework
- Built-in async support
- Automatic API docs
- Type safety with Pydantic

### Why Twilio?
- Industry-standard voice platform
- Simple webhook integration
- Built-in recording and TTS
- Global phone number coverage

### Why OpenAI Whisper?
- Best-in-class speech recognition
- Supports 99+ languages
- Simple API
- Cost-effective ($0.006/min)

### Why GPT-4?
- Advanced reasoning capabilities
- Excellent context understanding
- Handles nuanced questions
- Can follow instructions precisely

### Why FAISS?
- Fast similarity search (C++ core)
- Memory-efficient
- No external database needed
- Easy to serialize/deserialize

### Why OpenAI Embeddings?
- High quality (1536 dimensions)
- Fast API
- Consistent with GPT-4
- Good for semantic search

## Scalability Considerations

### Current Architecture (Single Instance)
- **Handles**: ~10 concurrent calls
- **Bottleneck**: LLM API rate limits
- **Storage**: In-memory vector store + disk

### Scaling Options

#### Horizontal Scaling
```
Load Balancer
    │
    ├──▶ App Server 1 (shared vector store)
    ├──▶ App Server 2 (shared vector store)
    └──▶ App Server 3 (shared vector store)
```

#### Improvements for Production
1. **Vector Store**: Move to Pinecone/Weaviate for distributed access
2. **Caching**: Redis for frequent queries
3. **Queue**: Celery for async processing
4. **Database**: PostgreSQL for call logs
5. **Monitoring**: Prometheus + Grafana
6. **CDN**: CloudFront for audio files

## Security Considerations

### Current Implementation
- ✅ Environment variables for secrets
- ✅ HTTPS required (via Twilio/ngrok)
- ✅ No authentication (webhook only)
- ✅ Input validation on form data

### Production Requirements
- [ ] Twilio signature verification
- [ ] Rate limiting per phone number
- [ ] Logging with PII redaction
- [ ] Admin authentication (if adding dashboard)
- [ ] API key rotation
- [ ] Audit trail

## Cost Breakdown

### Per-Call Costs
| Service | Cost | Notes |
|---------|------|-------|
| Twilio (inbound) | $0.0085/min | Voice minutes |
| Whisper API | $0.006/min | Transcription |
| OpenAI Embeddings | $0.0001 | Query embedding |
| GPT-4 | $0.03/call | ~1K tokens avg |
| Polly (optional) | $0.000004/char | Or use Twilio TTS (free) |
| **Total** | **~$0.05-0.10/call** | Depends on length |

### Monthly Costs (1000 calls/month)
- Infrastructure: $50-100
- API calls: $50-100
- Monitoring: $0-50
- **Total**: $100-250/month

### Cost Optimization Tips
1. Use GPT-3.5-turbo instead of GPT-4 (90% cheaper)
2. Cache frequent queries
3. Use Twilio's built-in TTS
4. Batch embedding creation during ingestion
5. Set max call length limits

## Future Architecture Enhancements

### Phase 2: State Management
```
[Redis] ← Session state
    ↓
[App Server] → Multi-turn conversations
```

### Phase 3: Analytics
```
[Call Events] → [Event Stream] → [Data Warehouse]
                                       ↓
                                  [BI Dashboard]
```

### Phase 4: Multi-Channel
```
[Voice] ─┐
[SMS]   ─┤→ [Unified Agent] → [Response]
[Chat]  ─┘
```

## Monitoring and Observability

### Key Metrics to Track
- Call volume (per hour/day)
- Response latency (P50, P95, P99)
- Error rates (by component)
- API costs (by service)
- Transcription accuracy (manual review)
- User satisfaction (feedback loop)

### Logging Strategy
```python
# Current: Structured logging
logger.info("User said: %s", transcribed_text)
logger.info("Retrieved %d chunks", len(chunks))
logger.info("Generated response: %s", ai_response)

# Production: Add context
logger.info("call_processing", extra={
    "call_sid": call_sid,
    "org_name": org_name,
    "duration_ms": duration,
    "components": ["stt", "rag", "llm"],
    "costs": {"whisper": 0.006, "gpt4": 0.03}
})
```

## Testing Strategy

### Current Tests
- ✅ Module imports
- ✅ Config loading
- ✅ Document chunking
- ✅ Vector store ops
- ✅ API endpoints

### Additional Test Coverage
- [ ] Unit tests per module
- [ ] Integration tests with mocks
- [ ] Load testing (locust)
- [ ] E2E tests with Twilio test credentials
- [ ] Regression tests for RAG quality

---

**Last Updated**: January 3, 2026  
**Version**: 1.0  
**Status**: Production-ready for basic use cases
