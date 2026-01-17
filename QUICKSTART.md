# ⚡ Quick Start Guide

Get Synapse Council running in 5 minutes.

## 1. Start Backend (Terminal 1)

```bash
cd backend
python -m venv venv
venv\Scripts\activate         # Windows
# source venv/bin/activate    # Mac/Linux
pip install -r requirements.txt
python api.py
```

Backend runs at: **http://localhost:8000**

## 2. Start Frontend (Terminal 2)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: **http://localhost:3000**

## 3. Use the App

1. Open http://localhost:3000
2. Type your decision question
3. Adjust agent weights (optional)
4. Click "Run Synapse Council"
5. View your personalized decision analysis

---

## Troubleshooting

**Backend won't start?**
- Install LangGraph dependencies used by agents
- Set any required API keys in environment

**Frontend won't start?**
- Ensure Node.js 18+ is installed
- Delete `node_modules` and run `npm install` again

**Can't connect?**
- Make sure both servers are running
- Check ports 8000 and 3000 are not in use

---

See [README.md](./README.md) for full documentation.
