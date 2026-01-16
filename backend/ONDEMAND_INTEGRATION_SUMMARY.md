# Synapse Council - On-Demand Platform Integration Summary

## What Was Done

Your Synapse Council backend has been fully updated to use the **On-Demand platform** instead of direct OpenAI API keys. This gives you access to multiple AI tools through a single unified platform.

## Key Changes

### 1. **New On-Demand Client** (`app/ondemand_client.py`)
   - Unified interface for all On-Demand services
   - Supports GPT, Gita, Audio, and Vision agents
   - Async/await architecture for better performance
   - Session management and conflict analysis

### 2. **Updated Configuration** (`app/config.py`)
   - Changed default provider from "ollama" to "ondemand"
   - Added On-Demand API key configuration
   - Agent ID configuration for each service:
     - GPT agent (main reasoning)
     - Gita guide (dharmic wisdom)
     - Audio transcription
     - Image/vision analysis
     - Conflict analyzer

### 3. **Refactored Components**

   **Counsellor Chat** (`app/counsellor.py`)
   - Now uses On-Demand GPT instead of OpenAI
   - Session memory still works as before
   - Optional user API key override
   - Better error handling

   **Multimodal Input** (`app/multimodal.py`)
   - Voice transcription via On-Demand audio agent
   - Image analysis via On-Demand vision agent
   - Falls back to platform key if user key not provided

   **Gita Guide Agent** (`app/agents/gita_guide.py`)
   - Enhanced to support both Ollama and On-Demand
   - New async method for On-Demand queries
   - Returns structured dharma-based guidance

### 4. **Environment Configuration** (`.env.example`)
   - New template with On-Demand settings
   - Detailed comments for each configuration option
   - Example agent IDs

### 5. **Documentation** (`ONDEMAND_SETUP.md`)
   - Complete setup guide
   - Feature overview
   - API endpoint documentation
   - Troubleshooting tips
   - Migration guide from OpenAI

## How to Use

### Step 1: Get On-Demand API Key
1. Visit https://on-demand.io
2. Create an account
3. Generate your API key
4. Keep it secure!

### Step 2: Configure Backend
```bash
cd backend
cp .env.example .env

# Edit .env and add:
ON_DEMAND_API_KEY=your_api_key_here
LLM_PROVIDER=ondemand
```

### Step 3: Install Dependencies
```bash
pip install httpx  # Required for async HTTP to On-Demand
```

### Step 4: Run Backend
```bash
uvicorn app.main:app --reload
```

## What You Get

### 1. **GPT-Based Decision Analysis**
   - Parse complex dilemmas
   - Generate agent perspectives
   - Facilitate council debates
   - Provide recommendations

### 2. **Bhagavad Gita Wisdom** 🙏
   - **Relevant shlokas** with Sanskrit and English
   - **Dharma analysis** - alignment with righteous duty
   - **Karma implications** - consequences and spiritual impact
   - **Core teachings** - philosophical guidance

   Example Output:
   ```json
   {
     "recommendation": "PROCEED",
     "confidence_score": 0.85,
     "relevant_shlokas": "2:47 - Karmanya va adhikara te ma phaleshu kadachana",
     "dharma_analysis": "This decision aligns with your professional dharma...",
     "karma_implications": "This action generates positive karmic debt...",
     "core_teaching": "The Gita teaches that action without attachment..."
   }
   ```

### 3. **Multimodal Input**
   - **Voice**: Upload audio, get transcription
   - **Images**: Upload photos/documents for analysis
   - **Text**: Traditional decision descriptions

### 4. **Session-Aware Counsellor**
   - Remembers past decisions
   - Provides continuity across sessions
   - Context-aware responses

## Supported AI Tools on On-Demand

| Tool | Purpose | Agent ID |
|------|---------|----------|
| GPT-4o / GPT-5.x | Decision reasoning, debate facilitation | `predefined-openai-gpt4o` |
| Bhagavad Gita | Dharmic wisdom, ethical guidance | `gita-guide` |
| Audio Transcription | Voice to text conversion | `audio-transcription` |
| Vision/Image Analysis | Analyze photos, documents, charts | `vision-analyzer` |
| Conflict Analyzer | Resolve debate perspectives | `conflict-analyzer` |
| Custom Agents | Your specialized tools | Custom IDs |

## API Endpoints (Unchanged - Better Powered)

All existing API endpoints now use On-Demand:

```
POST /api/decide          - Council debate with Gita wisdom
POST /api/counsellor/chat - Session-aware counseling
POST /api/transcribe      - Voice transcription
POST /api/upload-image    - Image analysis
GET  /health              - Health check
```

## Migration Benefits

✅ **Flexibility**: Access multiple AI tools with one API key
✅ **Gita Integration**: Dedicated dharmic wisdom agent
✅ **Unified**: No need for separate OpenAI, audio, and image APIs
✅ **Scalability**: On-Demand handles scaling
✅ **Security**: Single secure API key to manage
✅ **Cost Control**: Transparent per-call pricing

## Backward Compatibility

- You can still use Ollama locally by changing `LLM_PROVIDER=ollama`
- Frontend code is unchanged
- Database schema is unchanged
- Session memory still works exactly the same

## Files Modified

- ✅ `app/config.py` - Added On-Demand settings
- ✅ `app/counsellor.py` - Uses On-Demand now
- ✅ `app/multimodal.py` - Uses On-Demand agents
- ✅ `app/agents/gita_guide.py` - Dual mode support
- ✅ `app/main.py` - Enhanced logging
- ✅ `.env.example` - Updated template

## Files Created

- ✅ `app/ondemand_client.py` - New On-Demand client (380+ lines)
- ✅ `ONDEMAND_SETUP.md` - Complete setup guide

## Troubleshooting

**Error: "ON_DEMAND_API_KEY environment variable not set"**
→ Check your `.env` file has `ON_DEMAND_API_KEY=your_key`

**Error: "Failed to connect to On-Demand API"**
→ Check your API key is valid and internet connection works

**Slow responses**
→ Cloud-based services are slower than local Ollama; this is normal

**Agent not found**
→ Verify agent ID exists in your On-Demand dashboard

## Next Steps

1. ✅ Update backend with On-Demand client ← **Done!**
2. Create On-Demand account at https://on-demand.io
3. Configure API key in `.env`
4. Restart backend: `uvicorn app.main:app --reload`
5. Test via frontend at `http://localhost:3000`

## Support Resources

- On-Demand Docs: https://docs.on-demand.io
- Setup Guide: Read `ONDEMAND_SETUP.md`
- Configuration: Edit `backend/.env`
- Logs: Run with `--log-level debug` for details

## Questions?

Refer to:
- `ONDEMAND_SETUP.md` - Complete guide
- `app/ondemand_client.py` - Implementation details
- `.env.example` - Configuration options
- Backend logs - `uvicorn` output

---

**Status**: ✅ Ready to use!
**Next Action**: Get your On-Demand API key and configure `.env`
