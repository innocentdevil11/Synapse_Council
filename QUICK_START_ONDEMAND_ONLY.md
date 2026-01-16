# ⚡ Quick Start: Synapse Council On-Demand Only Mode

## The Simple Version

Your Synapse Council system now uses **ONLY the On-Demand platform**. No Ollama. No Gemini. Just On-Demand.

---

## 🚀 Start Everything

### 1. Backend (One command)
```powershell
cd c:\Users\Asus\Synapse_Council\backend
$env:PYTHONPATH="c:\Users\Asus\Synapse_Council\backend"
python -m uvicorn app.main:app --reload
```

**What you should see:**
```
LLM Provider: ondemand
Using On-Demand platform for ALL AI services
Application startup complete.
```

✅ If you see that, you're good!

### 2. Frontend
```powershell
cd c:\Users\Asus\Synapse_Council\frontend
npm start
```

Open: http://localhost:3000

**Notice**: No API key field! ✅

---

## 📝 Configuration

Your `.env` file should have:

```env
LLM_PROVIDER=ondemand
ON_DEMAND_API_KEY=Qb94qMlV3RbnYSdf7XhdOlHYhSNvBeWe
ON_DEMAND_BASE_URL=https://api.on-demand.io
ON_DEMAND_GPT_AGENT=tool-1717503940
ON_DEMAND_GITA_AGENT=tool-1717503940
ON_DEMAND_AUDIO_AGENT=tool-1713958830
ON_DEMAND_VISION_AGENT=tool-1712327325
```

That's it! (Don't worry about OLLAMA_* or GEMINI_* - they're ignored)

---

## ✨ What's Changed

### Before
- Ollama fallback if On-Demand failed
- API key optional in frontend
- Multiple provider options
- Confusing configuration

### After (Now)
- **Only On-Demand** - no fallbacks
- **No API key needed in frontend** - it uses backend key automatically
- **One provider** - simple and consistent
- **Backend validates everything** - app won't start without proper config

---

## 🧠 System at a Glance

```
Frontend (React)
    ↓ (no API key needed)
Backend (FastAPI)
    ↓ (uses ON_DEMAND_API_KEY from .env)
All 6 Agents + Counsellor + Multimodal
    ↓
On-Demand Platform (ONE ONLY)
    ├─ GPT (used by 5 agents, counsellor, memory)
    ├─ Gita (dharmic guidance)
    ├─ Audio (voice → text)
    └─ Vision (image analysis)
```

---

## ⚙️ The 6 Agents (All On-Demand)

1. **Risk Logic** - Probability, downside risk → On-Demand GPT
2. **EQ Advocate** - Emotions, relationships → On-Demand GPT
3. **Values Guard** - Values alignment → On-Demand GPT
4. **Red Team** - Contrarian perspective → On-Demand GPT
5. **Gita Guide** - Dharmic wisdom → On-Demand Gita
6. **Head Council** - Final verdict → On-Demand GPT

All 6 run **simultaneously** and debate. Head Council synthesizes final answer.

---

## 🎯 Decision Flow

```
Frontend submits decision
    ↓
Backend receives request (NO API key needed)
    ↓
Orchestrator launches 6 agents in parallel
    ├─ Risk: "Block - 30% downside"
    ├─ EQ: "Caution - emotional risk"
    ├─ Values: "Block - not aligned"
    ├─ Red Team: "Proceed - opposite view"
    ├─ Gita: "Caution - dharmic concern"
    └─ Head Council: Synthesizes...
    ↓
"CAUTION - Head Council verdict"
    ↓
Frontend displays results
```

All using On-Demand platform exclusively ✅

---

## 💬 Counsellor Chat

1. Type a message in chat
2. On-Demand GPT processes it
3. System remembers past decisions
4. Returns personalized advice

No API key needed. No configuration. Just works.

---

## 🔊 Voice & Image

### Upload an image
```
Decision: "Should I take this job?"
Image: Job offer screenshot
```

On-Demand Vision Agent analyzes the image.

### Transcribe voice
```
[Speak your decision...]
```

On-Demand Audio Agent transcribes to text, then all 6 agents analyze.

---

## ✅ Verification

### Quick check: Is backend working?

```powershell
curl http://localhost:8000/api/health
```

Or visit: http://localhost:8000/docs

### Full test: Submit a decision

1. Frontend: Type a decision
2. Watch backend logs - you should see:
   ```
   Risk Logic analysis complete
   EQ Advocate analysis complete
   Values Guard analysis complete
   Red Team analysis complete
   Gita Guide analysis complete
   Head Council judgment: [VERDICT]
   ```
3. Frontend displays results

---

## 🆘 Troubleshooting

### Backend won't start
```
Error: "LLM_PROVIDER must be 'ondemand'"
```
→ Check `.env` has `LLM_PROVIDER=ondemand`

### Backend won't start
```
Error: "ON_DEMAND_API_KEY is required"
```
→ Check `.env` has valid `ON_DEMAND_API_KEY=...`

### Decision submission returns error
```
Connection to On-Demand failed
```
→ Check ON_DEMAND_API_KEY is valid and internet connection works

### Frontend shows "Cannot reach backend"
→ Make sure backend is running on http://localhost:8000

---

## 📊 Architecture (One Picture)

```
┌─────────────────┐
│ Frontend (3000) │ ← No API key!
└────────┬────────┘
         │
    Backend (8000)
         │
    ┌────┴─────┐
    │ Decision │
    │ Received │
    └────┬─────┘
         │
    ┌────┴───────────────────────────────┐
    │ 6 Agents Run in Parallel           │
    │ (All using On-Demand)              │
    │ ├─ Risk Logic    ──→ On-Demand GPT │
    │ ├─ EQ Advocate   ──→ On-Demand GPT │
    │ ├─ Values Guard  ──→ On-Demand GPT │
    │ ├─ Red Team      ──→ On-Demand GPT │
    │ ├─ Gita Guide    ──→ On-Demand Gita│
    │ └─ Head Council  ──→ On-Demand GPT │
    └────┬──────────────────────────────┘
         │
    ┌────┴──────────┐
    │ Results Back  │
    │ to Frontend   │
    └───────────────┘
```

**That's it.** One provider. All working.

---

## 📋 Configuration Reference

| Setting | Value | Purpose |
|---------|-------|---------|
| `LLM_PROVIDER` | `ondemand` | Forces On-Demand only |
| `ON_DEMAND_API_KEY` | `your-key` | Authentication |
| `ON_DEMAND_BASE_URL` | `https://api.on-demand.io` | API endpoint |
| `ON_DEMAND_GPT_AGENT` | `tool-1717503940` | Default AI agent |
| `ON_DEMAND_GITA_AGENT` | `tool-1717503940` | Gita wisdom |
| `ON_DEMAND_AUDIO_AGENT` | `tool-1713958830` | Voice transcription |
| `ON_DEMAND_VISION_AGENT` | `tool-1712327325` | Image analysis |
| `ENABLE_LONG_TERM_MEMORY` | `true` | Remember past decisions |

---

## 🔑 Key Points

✅ **One Provider**: Only On-Demand  
✅ **Simple Config**: Just set env vars  
✅ **No Frontend API Key**: Backend handles auth  
✅ **Automatic Fallback**: None - we fail fast if On-Demand down  
✅ **All Agents on On-Demand**: 100% consistent  
✅ **Production Ready**: Tested and verified  

---

## 🚀 You're Ready!

Backend is running on On-Demand. Frontend works without API keys. All 6 agents are talking to On-Demand.

**Status: ✅ ON-DEMAND ONLY MODE ACTIVE**

Go submit some decisions! 🎯

---

Created: January 16, 2026  
Last Updated: After backend verification  
Status: Production Ready ✅
