# Quick Start: On-Demand Integration

## 🚀 5-Minute Setup

### 1. Get API Key (2 minutes)
```bash
# Visit https://on-demand.io
# Sign up → Create account → Generate API key
# Copy your API key
```

### 2. Configure Backend (2 minutes)
```bash
cd backend

# Create .env file
cp .env.example .env

# Edit .env - add your API key
# LLM_PROVIDER=ondemand
# ON_DEMAND_API_KEY=your_api_key_here
```

### 3. Install Dependencies (1 minute)
```bash
pip install httpx
```

### 4. Run Backend
```bash
cd backend
uvicorn app.main:app --reload
```

You should see:
```
INFO:     LLM Provider: ondemand
INFO:     Using On-Demand platform for AI services
INFO:     Orchestrator and Counsellor initialized successfully
```

## 🎯 What You Can Do Now

### 1. **Decision Council (AI Debate)**
```bash
curl -X POST http://localhost:8000/api/decide \
  -H "Content-Type: application/json" \
  -d '{
    "dilemma": "Should I change careers?",
    "context": "I have 10 years in finance, but want to explore tech"
  }'
```

### 2. **Counsellor Chat (Session Memory)**
```bash
curl -X POST http://localhost:8000/api/counsellor/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-123",
    "message": "Tell me about this job opportunity"
  }'
```

### 3. **Voice Input (Audio Transcription)**
```bash
curl -X POST http://localhost:8000/api/transcribe \
  -F "audio_file=@your_audio.mp3"
```

### 4. **Image Analysis (Vision)**
```bash
curl -X POST http://localhost:8000/api/upload-image \
  -F "image_file=@contract.png" \
  -F "context=Employment contract review"
```

## 📚 Key Features

| Feature | Description | API |
|---------|-------------|-----|
| **Council Debate** | Multi-agent AI decision analysis | `POST /api/decide` |
| **Gita Wisdom** 🙏 | Dharmic guidance from Bhagavad Gita | Included in `/api/decide` |
| **Counsellor** | Session-aware conversational AI | `POST /api/counsellor/chat` |
| **Voice** | Audio transcription to text | `POST /api/transcribe` |
| **Vision** | Image and document analysis | `POST /api/upload-image` |

## 🔍 What's Different from OpenAI

**Before (OpenAI):**
- Required user's own OpenAI API key
- Limited to GPT only
- No Bhagavad Gita wisdom agent
- Separate services for audio/images

**After (On-Demand):**
- ✅ Single platform API key
- ✅ Access to GPT, Gita, Audio, Vision agents
- ✅ Dedicated Bhagavad Gita wisdom
- ✅ Unified multimodal interface
- ✅ Better cost management

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| `ON_DEMAND_API_KEY not set` | Check `.env` file has your key |
| Connection error | Verify API key is valid; check internet |
| Slow responses | Cloud-based; normal for On-Demand |
| Agent not found | Check agent ID in On-Demand dashboard |

## 📖 Learn More

- **Full Setup Guide**: Read `ONDEMAND_SETUP.md`
- **Integration Details**: Check `ONDEMAND_INTEGRATION_SUMMARY.md`
- **Code**: See `app/ondemand_client.py`
- **On-Demand Docs**: https://docs.on-demand.io

## 🎓 Example: Get Gita Wisdom

When you call `/api/decide`, the Gita Guide Agent responds with:

```json
{
  "agent_name": "Gita Guide",
  "recommendation": "PROCEED",
  "confidence_score": 0.85,
  "reasoning": "This decision aligns with your dharma...",
  "relevant_shlokas": "2:47 - Karmanya va adhikara te ma phaleshu kadachana",
  "dharma_analysis": "As a professional, your duty is to develop your skills...",
  "karma_implications": "This choice will generate positive karmic fruit...",
  "core_teaching": "The Gita teaches that we should act with full commitment..."
}
```

## ✅ Verification Checklist

- [ ] On-Demand account created
- [ ] API key generated and copied
- [ ] `.env` file updated with key
- [ ] `httpx` installed: `pip install httpx`
- [ ] Backend runs: `uvicorn app.main:app --reload`
- [ ] Frontend connects: `http://localhost:3000`

## 🚀 You're Ready!

Your Synapse Council is now powered by On-Demand with:
- ✅ GPT-based decision analysis
- ✅ Bhagavad Gita wisdom
- ✅ Multimodal input (voice, images)
- ✅ Session-aware counseling
- ✅ Unified platform

Start your decision-making journey! 🙏
