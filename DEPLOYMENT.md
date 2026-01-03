# 🚀 Deployment Guide

## Quick Start: Deploy to Railway (Easiest)

### Prerequisites
- GitHub account
- Railway account (free): [railway.app](https://railway.app)
- Your API keys ready

### Step 1: Push to GitHub

```bash
cd /Users/anuj/Desktop/voice_agent/ai-voice-calling-agent

# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit"

# Create GitHub repo and push
gh repo create SamparkX --public --source=. --push
# OR manually: create repo on github.com and push
```

### Step 2: Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Click **"Start a New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `SamparkX` repository
5. Railway will auto-detect the `railway.toml` file

### Step 3: Add Environment Variables

In Railway dashboard, add:
```
OPENAI_API_KEY=sk-proj-IEBbEshC2_sB4hm96YkE...
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
```

### Step 4: Deploy!

Railway will automatically:
- ✅ Build your app
- ✅ Run document ingestion
- ✅ Start the server
- ✅ Give you a public URL (e.g., `https://samparkx.up.railway.app`)

### Step 5: Configure Twilio

1. Go to Twilio Console → Phone Numbers
2. Set webhook: `https://your-railway-url.up.railway.app/voice/inbound`
3. Method: POST
4. Save!

---

## Option 2: Deploy to Render.com

### Steps:

1. **Push to GitHub** (same as above)

2. **Go to [render.com](https://render.com)**

3. **New Web Service** → Connect GitHub

4. **Configure:**
   - Name: `samparkx-voice-agent`
   - Region: `Oregon (US West)`
   - Branch: `main`
   - Build Command: `pip install -r requirements.txt && python scripts/ingest_documents_free.py --org sample_org`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. **Add Environment Variables** (same as Railway)

6. **Deploy!**

**Free Tier**: 750 hours/month (enough for testing)

---

## Option 3: Deploy with Docker Locally

### Test Docker Build:

```bash
cd /Users/anuj/Desktop/voice_agent/ai-voice-calling-agent

# Build image
docker build -t samparkx-voice-agent .

# Run locally
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="your_key" \
  -e TWILIO_ACCOUNT_SID="your_sid" \
  -e TWILIO_AUTH_TOKEN="your_token" \
  samparkx-voice-agent

# Test
curl http://localhost:8000/health
```

### Deploy to Cloud:

**Google Cloud Run:**
```bash
# Install gcloud
brew install google-cloud-sdk

# Login
gcloud auth login

# Deploy
gcloud run deploy samparkx-voice-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY="your_key"
```

---

## Option 4: AWS EC2 (Traditional VPS)

### Setup:

1. **Launch EC2 Instance**
   - Instance type: `t3.small` or `t3.medium`
   - OS: Ubuntu 22.04 LTS
   - Security Group: Allow ports 22, 80, 443, 8000

2. **SSH and Setup:**

```bash
# SSH to instance
ssh -i your-key.pem ubuntu@ec2-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python & dependencies
sudo apt install python3-pip python3-venv nginx -y

# Clone repository
git clone https://github.com/anujky576/SamparkX.git
cd SamparkX/ai-voice-calling-agent

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
# Add your API keys

# Ingest documents
python scripts/ingest_documents_free.py --org sample_org

# Install Ollama (for local LLM)
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.2:3b

# Run with gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

3. **Setup Nginx Reverse Proxy:**

```bash
sudo nano /etc/nginx/sites-available/samparkx

# Add:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/samparkx /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

4. **Setup SSL with Let's Encrypt:**

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

5. **Setup as System Service:**

```bash
sudo nano /etc/systemd/system/samparkx.service

# Add:
[Unit]
Description=SamparkX Voice Agent
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/SamparkX/ai-voice-calling-agent
Environment="PATH=/home/ubuntu/SamparkX/ai-voice-calling-agent/.venv/bin"
ExecStart=/home/ubuntu/SamparkX/ai-voice-calling-agent/.venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable samparkx
sudo systemctl start samparkx
sudo systemctl status samparkx
```

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid | Best For |
|----------|-----------|------|----------|
| **Railway** | $5 credit/mo | $5-20/mo | Quick start, hobby |
| **Render** | 750 hrs/mo | $7+/mo | Small projects |
| **Google Cloud Run** | 2M requests | Pay per use | Variable traffic |
| **AWS EC2** | 1 year free | $10-50/mo | Full control |
| **DigitalOcean** | None | $6-12/mo | Simple, predictable |
| **Vercel** | Limited | $20/mo | Edge functions |

---

## ⚡ Performance Considerations

### For Production:

**If using Ollama locally on server:**
- Need at least 8GB RAM
- AWS t3.large ($60/mo) or higher
- Or use OpenAI API (faster, more expensive)

**If using only OpenAI APIs:**
- Can use smaller instances
- Railway/Render free tier is enough
- Better latency (~2-3 sec responses)

**Recommended for your case:**
- Start: Railway (free tier)
- Test with your university data
- If scaling needed: AWS EC2 with Ollama

---

## 🔒 Security Checklist

Before going live:

```bash
# 1. Never commit .env to git
echo ".env" >> .gitignore

# 2. Use environment variables for secrets
# Set in Railway/Render dashboard, not in code

# 3. Enable HTTPS (handled by Railway/Render automatically)

# 4. Add rate limiting
pip install slowapi

# 5. Monitor logs
# Railway/Render have built-in logging
```

---

## 🧪 Test Your Deployment

After deployment:

```bash
# 1. Health check
curl https://your-app.up.railway.app/health

# 2. Make test call (Twilio)
# Call your Twilio number and test

# 3. Check logs
# In Railway/Render dashboard

# 4. Test query via UI
# Deploy Streamlit UI separately or use API directly
```

---

## 📊 Monitoring

### Railway/Render (Built-in)
- View logs in dashboard
- Monitor CPU/Memory usage
- Track deployments

### Custom Monitoring
```bash
# Add Sentry for error tracking
pip install sentry-sdk

# In app/main.py:
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

---

## 🚀 Next Steps

1. **Push code to GitHub**
2. **Deploy to Railway** (5 minutes)
3. **Add environment variables**
4. **Configure Twilio webhook**
5. **Make test call!**

**Your app will be live at:**
`https://samparkx.up.railway.app` (or similar)

---

## 🆘 Troubleshooting

### Common Issues:

**Port Error:**
```python
# Make sure your app uses $PORT environment variable
# Railway/Render inject PORT automatically
# FastAPI defaults to 8000, but they need dynamic port
```

**Vector Store Missing:**
```bash
# Ensure ingestion runs during build
# Add to Render build command:
python scripts/ingest_documents_free.py --org sample_org
```

**Ollama Not Working:**
```bash
# Ollama requires separate server or local machine
# For cloud: Use OpenAI API instead
# Or: Deploy Ollama on separate container
```

---

## Need Help?

- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
- Your FastAPI app: https://fastapi.tiangolo.com
- Twilio Webhooks: https://www.twilio.com/docs/usage/webhooks

Ready to deploy? Run:
```bash
git push origin main
```

Then connect to Railway! 🚀
