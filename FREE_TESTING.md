# 🆓 Free Testing Guide

## Get Started with ZERO Cost

### Step 1: Get Free OpenAI API Key

1. **Sign up for OpenAI** (if you don't have an account):
   - Go to https://platform.openai.com/signup
   - New accounts get **$5-18 in free credits**
   - Valid for 3 months

2. **Create API key**:
   - Visit https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy the key (starts with `sk-...`)

3. **Add to your project**:
   ```bash
   echo "OPENAI_API_KEY=sk-your-key-here" > .env
   ```

### Step 2: Test WITHOUT Real Phone Calls

You can test the entire AI pipeline without spending a cent on Twilio:

```bash
# 1. Start the project
./start.sh

# 2. Test all components (FREE)
python scripts/test_pipeline.py

# 3. Test document ingestion (FREE)
python scripts/ingest_documents.py --org sample_org

# 4. Test API endpoints (FREE)
curl http://localhost:8000/health
curl -X POST http://localhost:8000/voice/inbound
```

### Step 3: Simulate the Voice Pipeline

Test the core AI logic without making real calls:

```python
# Create: test_without_calls.py

import sys
sys.path.append('.')

from app.llm.responder import generate_response
from app.rag.retrieve import retrieve_relevant_chunks

# Simulate user question
user_question = "What are your operating hours?"

# Test RAG retrieval
print("🔍 Searching knowledge base...")
chunks = retrieve_relevant_chunks(user_question, k=3)
print(f"Found {len(chunks)} relevant chunks")

# Test LLM response
print("\n🤖 Generating AI response...")
response = generate_response(user_question, chunks)
print(f"\n✅ Response: {response}")
```

Run it:
```bash
python test_without_calls.py
```

**Cost: $0.00** (uses ~500 tokens = $0.0015)

### Step 4: Test Real Calls (When Ready)

When you want to test with actual phone calls:

1. **Get Twilio Free Trial**:
   - Sign up at https://www.twilio.com/try-twilio
   - Get **$15 free credit** (no credit card required initially)
   - Get a free trial phone number

2. **Add Twilio credentials to `.env`**:
   ```bash
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

3. **Use ngrok for testing** (FREE):
   ```bash
   # Install ngrok
   brew install ngrok
   
   # Expose local server
   ngrok http 8000
   
   # Copy the https URL to Twilio webhook
   ```

4. **Make test calls**:
   - Call your Twilio number
   - Test with 10-20 calls to validate
   - Free credit covers 100+ calls

## 💰 Cost Breakdown for Free Testing

### OpenAI Free Credits ($5-18)
| Action | Tokens | Cost | Quantity with $5 |
|--------|--------|------|------------------|
| Document ingestion | 1K | $0.0001 | 50,000 docs |
| Query embedding | 100 | $0.00001 | 500,000 queries |
| GPT-4 response | 1K | $0.03 | 166 responses |
| Whisper (1 min) | - | $0.006 | 833 minutes |
| **Full call** | - | **$0.05** | **100 calls** |

### Twilio Free Trial ($15)
- **Inbound calls**: ~1,500 minutes free
- **Test phone number**: FREE during trial
- **SMS**: 100+ free messages

## 🎯 Recommended Testing Path

### Week 1: Local Development (FREE)
```bash
# Day 1: Setup
./start.sh
python scripts/test_pipeline.py

# Day 2: Test document processing
cp your-docs.pdf data/sample_org/knowledge/
python scripts/ingest_documents.py --org sample_org

# Day 3: Test AI responses
python test_without_calls.py

# Day 4-5: Customize for your use case
# Edit config.json, add more documents
```

**Cost so far: $0.00 - $0.50**

### Week 2: Voice Testing (FREE)
```bash
# Day 6: Setup Twilio trial
# Get free phone number

# Day 7: Make test calls
# Use ngrok + make 10-20 test calls
```

**Cost: $0.50 - $1.00** (from Twilio free credit)

### Week 3: Production Ready (Still Cheap)
- Deploy to cloud
- Use real phone numbers
- Monitor actual usage

**Cost: $50-100/month** (only after you go live)

## 🛠️ Alternative: Test Without OpenAI

If you want to test the structure without ANY API costs:

### Option 1: Mock Mode

Create `test_mock.py`:
```python
# Mock all API calls for testing structure

def mock_transcribe(audio_url):
    return "What are your operating hours?"

def mock_embed(text):
    return [0.1] * 1536  # Fake embedding

def mock_generate(query, context):
    return "We are open Monday-Friday 9 AM - 5 PM"

# Test the flow
print("📞 Simulating call...")
transcription = mock_transcribe("fake_url")
print(f"🎤 Transcribed: {transcription}")

embedding = mock_embed(transcription)
print(f"🔢 Embedded: {len(embedding)} dimensions")

response = mock_generate(transcription, ["context1", "context2"])
print(f"🤖 Response: {response}")
```

### Option 2: Use Local Models (Advanced)

Replace OpenAI with free local alternatives:
- **Whisper**: Run locally (needs good GPU)
- **LLM**: Use Ollama with Llama 3
- **Embeddings**: Use sentence-transformers

**Pros**: 100% free forever  
**Cons**: Complex setup, slower, lower quality

## 📊 What's Actually FREE Forever

1. ✅ **FastAPI server** - FREE
2. ✅ **Document processing** - FREE
3. ✅ **FAISS vector store** - FREE
4. ✅ **Code structure** - FREE
5. ✅ **Local testing** - FREE
6. ✅ **Development** - FREE

## 💵 What Costs Money (Pay-as-you-go)

1. 💰 **OpenAI APIs** - $0.05 per call average
2. 💰 **Twilio calls** - $0.01 per minute
3. 💰 **Cloud hosting** (optional) - $5-50/month
4. 💰 **Domain name** (optional) - $10/year

## 🎓 Student? Academic Discounts

- **OpenAI**: Often have academic programs
- **Twilio**: Education program available
- **AWS**: $100+ in free credits via GitHub Student Pack
- **Google Cloud**: $300 free credits for new users

## 🚀 Start NOW (Absolutely Free)

```bash
# 1. Get OpenAI free credits
# Visit: https://platform.openai.com/signup

# 2. Add your key
nano .env
# Add: OPENAI_API_KEY=sk-...

# 3. Start testing
./start.sh

# 4. Run tests
python scripts/test_pipeline.py

# 5. Test AI pipeline
python test_without_calls.py
```

## ✅ Free Testing Checklist

- [ ] OpenAI account created (free $5-18 credits)
- [ ] API key added to `.env`
- [ ] Server starts successfully
- [ ] Integration tests pass
- [ ] Document ingestion works
- [ ] Can query the knowledge base
- [ ] RAG retrieval returns relevant chunks
- [ ] LLM generates sensible responses
- [ ] Ready for voice testing with Twilio trial

## 🎉 Bottom Line

**You can build and test this entire project for FREE using:**
1. OpenAI free credits ($5-18)
2. Twilio free trial ($15)
3. Local development (FREE)

**Total cost for development: $0**  
**Total cost for 100 test calls: $0**  
**Only pay when you go to production!**

---

**Questions?**
- See main [README.md](README.md)
- Check [USAGE.md](USAGE.md) for detailed guides
