# On-Demand Platform Integration Guide

## Overview

Synapse Council now supports the **On-Demand** platform for seamless access to multiple AI tools:
- **GPT models** (GPT-4o, GPT-5.x) for reasoning and decision analysis
- **Bhagavad Gita wisdom** agent for ethical and dharmic guidance
- **Audio transcription** for voice input
- **Image analysis** (vision) for analyzing visual decision factors
- **Custom agents** for specialized tasks

## Setup Instructions

### 1. Get Your On-Demand API Key

1. Visit [https://on-demand.io](https://on-demand.io)
2. Sign up and create an account
3. Generate your API key from the dashboard
4. Copy the API key (keep it secure!)

### 2. Configure Your Backend

1. Copy the environment template:
   ```bash
   cp backend/.env.example backend/.env
   ```

2. Edit `backend/.env` and set:
   ```env
   LLM_PROVIDER=ondemand
   ON_DEMAND_API_KEY=your_api_key_here
   ON_DEMAND_BASE_URL=https://api.on-demand.io
   ```

3. Customize agent IDs if needed (optional):
   ```env
   ON_DEMAND_GPT_AGENT=predefined-openai-gpt4o
   ON_DEMAND_GITA_AGENT=gita-guide
   ON_DEMAND_AUDIO_AGENT=audio-transcription
   ON_DEMAND_VISION_AGENT=vision-analyzer
   ```

### 3. Install Dependencies

The On-Demand integration requires `httpx` for async HTTP requests:

```bash
cd backend
pip install httpx
# Or update your requirements.txt
pip install -r requirements.txt
```

### 4. Start the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

The backend will validate your On-Demand API key on startup. If there's an issue, check your `.env` file.

## Features

### GPT-Based Decision Analysis

The orchestrator uses On-Demand's GPT model for:
- Parsing complex dilemmas
- Generating agent perspectives
- Facilitating council debates
- Final recommendations

### Bhagavad Gita Wisdom

The specialized Gita Guide agent provides:
- **Relevant shlokas** (verses) from the Gita
- **Dharma analysis** - alignment with righteous duty
- **Karma implications** - karmic consequences
- **Core teachings** - philosophical guidance

Example response structure:
```json
{
  "recommendation": "PROCEED",
  "confidence_score": 0.85,
  "reasoning": "This decision aligns with Arjuna's duty...",
  "relevant_shlokas": "2:47 - Karmanya va adhikara te...",
  "dharma_analysis": "Your svadharma as a professional...",
  "karma_implications": "This action will generate positive karma...",
  "core_teaching": "The Gita teaches that..."
}
```

### Multimodal Input

#### Voice Transcription
```python
from app.multimodal import transcribe_voice

transcript = await transcribe_voice(
    audio_file_path="decision_memo.mp3"
    # Optionally pass user_api_key, or uses platform key
)
```

#### Image Analysis
```python
from app.multimodal import analyze_image

description, analysis = await analyze_image(
    image_file_path="contract_screenshot.png",
    context="Employment contract review"
)
```

### Session-Aware Counsellor Chat

The counsellor remembers past decisions and provides continuity:

```python
from app.counsellor import CounsellorChat

counsellor = CounsellorChat()

reply, memory_summary = await counsellor.chat(
    session_id="user-session-123",
    message="Should I accept this job offer?",
    user_api_key=None  # Uses platform key if not provided
)
```

## API Endpoints

### Decision Analysis (Council Mode)
```
POST /api/decide
Content-Type: application/json

{
  "dilemma": "Should I change careers?",
  "context": "I have 10 years in finance...",
  "user_api_key": "optional-for-override"
}
```

### Counsellor Chat (Session-Aware)
```
POST /api/counsellor/chat
Content-Type: application/json

{
  "session_id": "user-123-session",
  "message": "Tell me about this dilemma",
  "user_api_key": "optional-for-override"
}
```

### Voice Transcription
```
POST /api/transcribe
Content-Type: multipart/form-data

audio_file: <binary>
user_api_key: optional
```

### Image Analysis
```
POST /api/upload-image
Content-Type: multipart/form-data

image_file: <binary>
context: "What is this?"
user_api_key: optional
```

## Migration from OpenAI to On-Demand

If you were previously using direct OpenAI API keys:

### Before (OpenAI):
```env
# Each user needed their own OpenAI API key
OPENAI_API_KEY=sk-...
```

### After (On-Demand):
```env
# One platform API key supports all users
LLM_PROVIDER=ondemand
ON_DEMAND_API_KEY=your_api_key
```

### Benefits:
- ✅ Single API key for the platform
- ✅ Support for Bhagavad Gita wisdom
- ✅ Unified audio and image processing
- ✅ Better cost management
- ✅ Specialized agents for specific tasks

## Troubleshooting

### "ON_DEMAND_API_KEY not set" Error

**Solution:** Check your `.env` file:
```bash
# Verify the file exists
cat backend/.env

# Should contain:
ON_DEMAND_API_KEY=your_key_here
```

### "Cannot connect to On-Demand API"

**Solution:** Check:
1. Your API key is valid (test in on-demand dashboard)
2. Internet connection is available
3. On-Demand service is operational
4. Base URL is correct: `https://api.on-demand.io`

### Slow Response Times

**Solution:** 
- On-Demand requests may take longer than local Ollama
- This is normal for cloud-based services
- Adjust timeouts if needed in `ondemand_client.py`

### Specific Agent Not Available

**Solution:**
- Verify the agent ID exists in your On-Demand account
- Check `ON_DEMAND_GITA_AGENT` is correctly configured
- Test the agent directly in On-Demand dashboard

## Cost Management

On-Demand charges per API call. To optimize costs:

1. **Use appropriate models:**
   - Use GPT-4o for most tasks
   - Use GPT-5.x only for complex reasoning

2. **Batch requests:**
   - Group related analyses
   - Reuse session contexts

3. **Monitor usage:**
   - Check On-Demand dashboard for usage metrics
   - Set up billing alerts

## Advanced Configuration

### Using Multiple On-Demand Agents

Create custom agents in On-Demand for specialized tasks:

```python
from app.ondemand_client import OnDemandClient

client = OnDemandClient(api_key=settings.ON_DEMAND_API_KEY)

# Use custom agent
response = await client.chat(
    query="Your question here",
    agent_ids=["your-custom-agent-id"],
)
```

### Custom Model Configuration

Adjust temperature and token limits per request:

```python
response = await client.chat(
    query="Your question",
    agent_ids=["predefined-openai-gpt4o"],
    model_config={
        "temperature": 0.9,  # More creative
        "max_tokens": 2000,  # Longer responses
        "top_p": 0.95,
    },
)
```

## Support

For issues or questions:
1. Check On-Demand documentation: https://docs.on-demand.io
2. Review backend logs: `uvicorn app.main:app --log-level debug`
3. Verify configuration in `.env`
4. Contact On-Demand support if API issues persist

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│              Frontend (React)                           │
│  - Decision Input                                       │
│  - Counsellor Chat                                      │
│  - Results Display                                      │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│         Backend (FastAPI)                               │
│  - orchestrator.py (Debate engine)                      │
│  - counsellor.py (Session memory)                       │
│  - multimodal.py (Audio/Image)                          │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│    On-Demand Platform (Cloud)                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Available Agents:                               │   │
│  │ - GPT-4o / GPT-5.x (Decision reasoning)        │   │
│  │ - Gita-Guide (Dharmic wisdom)                  │   │
│  │ - Audio-Transcription (Voice → Text)           │   │
│  │ - Vision-Analyzer (Image analysis)             │   │
│  │ - Conflict-Analyzer (Debate resolution)        │   │
│  │ - Custom agents (As configured)                │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## FAQ

**Q: Do I need an On-Demand account if I want to use Ollama?**
A: No, you can still use `LLM_PROVIDER=ollama` with a local Ollama instance.

**Q: Can I switch between providers (Ollama ↔ On-Demand)?**
A: Yes! Just change `LLM_PROVIDER` in your `.env` file and restart.

**Q: Will my On-Demand API key be exposed?**
A: No, it's only used server-side in backend environment variables.

**Q: What happens if On-Demand is down?**
A: The API will return an error. Consider having a fallback LLM provider.

**Q: Can I use my own custom On-Demand agents?**
A: Yes! Modify the agent IDs in `.env` to point to your custom agents.
