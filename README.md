# Synapse Council

**Multi-Agent Personal Decision Copilot**

Replace binary AI answers with structured multi-agent debate. Submit a serious dilemma (career, investment, life decision), and four specialized agents analyze it from different lenses, debate each other, and synthesize a transparent, explainable recommendation.

---

## Features

✨ **Four Specialized Agents**
- **Risk & Logic**: Probabilistic outcomes, downside risk, failure modes, financial impact
- **EQ Advocate**: Emotional/psychological impact, burnout, relationships, identity, wellbeing
- **Values Guard**: Ethics, stakeholder impact, integrity, long-term values, second-order effects
- **Red Team**: Expose blind spots, challenge consensus, wild-card scenarios, overconfidence

✨ **Structured Multi-Agent Debate**
- All agents analyze in parallel (Round 0)
- LLM-powered semantic conflict scoring
- Adaptive debate rounds (1-2 rounds if agents disagree above threshold)
- Full audit trail of all rounds

✨ **Transparent Results**
- Final weighted recommendation (PROCEED / CAUTION / BLOCK)
- Confidence score based on agent agreement
- **Conflict Heatmap**: Visual 4x4 matrix showing agent agreement/disagreement
- Individual agent cards with full reasoning
- Customizable weights for each agent

✨ **Modern Web UI**
- React + TypeScript frontend
- Real-time loading states
- Interactive Plotly heatmap
- Responsive design (desktop & mobile)
- Dark mode theme

---

## Tech Stack

**Backend**
- Python 3.10+ / FastAPI (async)
- Google Gemini API (free tier: gemini-2.0-flash)
- Pydantic for type safety
- Uvicorn ASGI server

**Frontend**
- React 18 + TypeScript
- Plotly for conflict heatmap visualization
- CSS Grid for responsive layouts
- Fetch API for HTTP requests

**Deployment**
- Backend: Docker-ready (Render, Railway, Heroku)
- Frontend: Static build (Vercel, Netlify)
- Stateless MVP (no database)

---

## Quick Start

### For Windows Users

⚠️ **See [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for detailed Windows-specific instructions.**

### For macOS/Linux Users

#### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows

pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Start backend
uvicorn app.main:app --reload
```

Backend runs on `http://localhost:8000`

#### 2. Frontend Setup

Open a **new terminal**:

```bash
cd frontend
npm install
npm start
```

Frontend runs on `http://localhost:3000`

---

## Configuration

### Backend (.env)

```env
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.0-flash
FRONTEND_URL=http://localhost:3000
CONFLICT_THRESHOLD=0.2
MAX_DEBATE_ROUNDS=2
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1500
```

**Get your free Gemini API key**: https://aistudio.google.com/app/apikey

### Frontend (.env)

```env
REACT_APP_API_URL=http://localhost:8000
```

---

## API Endpoints

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "Synapse Council"
}
```

### Submit Decision

```bash
POST /api/decide
Content-Type: application/json

{
  "dilemma": "Should I leave my stable job to start a startup?",
  "context": "I have 6 months of savings and a growing family.",
  "weights": {
    "risk": 0.4,
    "eq": 0.2,
    "values": 0.3,
    "red_team": 0.1
  }
}
```

Response:
```json
{
  "recommendation": "CAUTION (Mixed signals)",
  "confidence_score": 0.78,
  "conflict_heatmap": {
    "risk_eq": 0.3,
    "risk_values": 0.1,
    "risk_red_team": 0.6,
    "eq_values": 0.8,
    "eq_red_team": 0.7,
    "values_red_team": 0.5
  },
  "agent_responses": {
    "risk": { "recommendation": "CAUTION", "confidence_score": 0.85, "reasoning": "...", ... },
    "eq": { "recommendation": "PROCEED", "confidence_score": 0.72, "reasoning": "...", ... },
    "values": { "recommendation": "CAUTION", "confidence_score": 0.80, "reasoning": "...", ... },
    "red_team": { "recommendation": "BLOCK", "confidence_score": 0.65, "reasoning": "...", ... }
  },
  "debate_rounds": 2,
  "audit_trail": [
    { "round": 0, "responses": {...}, "conflict_matrix": {...} },
    { "round": 1, "responses": {...}, "conflict_matrix": {...} }
  ],
  "execution_time_ms": 45230
}
```

---

## Project Structure

```
synapse-council/
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI app
│   │   ├── config.py                    # Settings
│   │   ├── schemas.py                   # Pydantic models
│   │   ├── llm_client.py                # Gemini wrapper
│   │   ├── orchestrator.py              # Multi-agent orchestrator
│   │   └── agents/
│   │       ├── base.py                  # Abstract agent class
│   │       ├── risk_logic.py            # Risk & Logic agent
│   │       ├── eq_advocate.py           # EQ Advocate agent
│   │       ├── values_guard.py          # Values Guard agent
│   │       └── red_team.py              # Red Team agent
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DecisionInput.tsx        # Form + sliders
│   │   │   ├── ResultsPanel.tsx         # Results layout
│   │   │   ├── ConflictHeatmap.tsx      # Plotly heatmap
│   │   │   ├── AgentCard.tsx            # Agent card
│   │   │   └── LoadingSpinner.tsx       # Loading state
│   │   ├── styles/
│   │   │   ├── *.css                    # Component styles
│   │   ├── App.tsx                      # Main app
│   │   ├── index.tsx                    # Entry point
│   │   ├── types.ts                     # TS interfaces
│   │   ├── api.ts                       # HTTP client
│   │   └── index.css                    # Global styles
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   └── tsconfig.json
│
├── WINDOWS_SETUP.md                      # Windows-specific guide
└── README.md                             # This file
```

---

## How It Works

### 1. User Submits Dilemma
User enters a decision and optional context, adjusts agent weights (importance).

### 2. Round 0: Initial Analysis
All four agents analyze in **parallel**:
- Risk & Logic agent generates its recommendation
- EQ Advocate generates its recommendation
- Values Guard generates its recommendation
- Red Team generates its recommendation

Each returns a JSON object with:
- `recommendation` (PROCEED / CAUTION / BLOCK)
- `confidence_score` (0-1)
- `reasoning` + role-specific fields

### 3. Conflict Scoring
System uses LLM to compute **semantic disagreement** between all 6 agent pairs:
- Requests: "Rate agreement between these two positions on 0-1 scale"
- Converts to conflict score: `1 - similarity`

### 4. Adaptive Debate (Optional)
If average conflict > threshold (0.2), runs 1-2 debate rounds:
- Pass previous agent responses to each agent
- Agents can revise/strengthen position
- Recompute conflict matrix
- Stop when: conflict < threshold OR max rounds reached

### 5. Synthesis
- Maps recommendations to scores: PROCEED=1.0, CAUTION=0.5, BLOCK=0.0
- Computes weighted sum using user weights
- Converts to final recommendation text
- Calculates confidence based on agent agreement

### 6. Response
Returns:
- Final recommendation text + confidence
- Conflict heatmap (6 pairwise conflicts)
- Full agent responses
- Number of debate rounds
- Audit trail (all rounds)

---

## Development

### Backend Tests

```bash
cd backend
source venv/bin/activate

# Manual test
curl -X POST http://localhost:8000/api/decide \
  -H "Content-Type: application/json" \
  -d '{
    "dilemma": "Should I change careers?",
    "weights": {"risk": 0.4, "eq": 0.3, "values": 0.2, "red_team": 0.1}
  }'
```

### Frontend Development

```bash
cd frontend
npm start          # Dev server with hot reload
npm run build      # Production build
npm test           # Run tests (if configured)
```

---

## Deployment

### Backend (Docker)

```bash
cd backend
docker build -t synapse-council .
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=sk-xxxxx \
  synapse-council
```

Deploy to Render, Railway, or Heroku.

### Frontend (Static)

```bash
cd frontend
npm run build
# Deploy 'build/' folder to Vercel, Netlify, or any static host
```

---

## Limitations & Future Work

### Current MVP (36-hour build)
- ✅ No user authentication
- ✅ Stateless (no database)
- ✅ Single model (Gemini)
- ✅ REST API only (no streaming)
- ✅ English only

### Future Enhancements
- [ ] User accounts & decision history
- [ ] Streaming LLM responses
- [ ] Multi-language support
- [ ] WebSocket real-time updates
- [ ] Advanced analytics dashboard
- [ ] Model fine-tuning
- [ ] Export decisions to PDF

---

## Contributing

This is an MVP. Contributions welcome! Areas for improvement:
- Better prompts for agents
- Additional agent personas
- Conflict scoring algorithm
- Frontend accessibility
- Test suite
- Documentation

---

## License

MIT

---

## Contact

Built as a 36-hour production MVP for the Synapse Council decision-making system.

Questions? Open an issue or submit a discussion.

---

## Acknowledgments

- Inspired by multi-agent systems and structured decision-making frameworks
- Uses Google Gemini for language understanding
- React & TypeScript for type-safe UI development
- Plotly for interactive visualizations