# Synapse Council - Windows Setup Guide

Complete instructions for running the full stack on Windows.

## Prerequisites

- **Python 3.10+** ([download](https://www.python.org/downloads/))
- **Node.js 18+** ([download](https://nodejs.org/))
- **Git** (optional, for cloning) ([download](https://git-scm.com/))
- **Gemini API Key** ([get free key](https://aistudio.google.com/app/apikey))

### Verify Installation

Open **PowerShell** or **Command Prompt** and run:

```bash
python --version
node --version
npm --version
```

---

## Project Setup

### 1. Clone or Extract the Project

Navigate to your desired location and extract the project folder:

```bash
cd C:\Users\YourUsername\Desktop
# (Or your preferred location)
```

### 2. Backend Setup

Open **PowerShell** in the `backend` folder:

```bash
cd synapse-council\backend
```

#### Create Virtual Environment

```bash
python -m venv venv
```

#### Activate Virtual Environment

```bash
.\venv\Scripts\Activate.ps1
```

**Note:** If you get an execution policy error, run:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then run the activation command again.

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the `backend` folder:

```bash
notepad .env
```

Paste this content and save:

```env
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.0-flash
FRONTEND_URL=http://localhost:3000
CONFLICT_THRESHOLD=0.2
MAX_DEBATE_ROUNDS=2
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1500
```

Replace `your-gemini-api-key-here` with your actual API key.

#### Test Backend

```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Visit `http://localhost:8000/health` in your browser to verify.

**Keep this terminal open!** (Don't close it while running the frontend)

---

### 3. Frontend Setup

Open a **new PowerShell/Command Prompt** window in the `frontend` folder:

```bash
cd synapse-council\frontend
```

#### Install Node Modules

```bash
npm install
```

This will install React, TypeScript, Plotly, and other dependencies.

#### Start Frontend Development Server

```bash
npm start
```

This will automatically open `http://localhost:3000` in your browser.

---

## Running the Application

You should now have **two terminal windows open**:

1. **Backend Terminal**: Running `uvicorn app.main:app --reload` on port 8000
2. **Frontend Terminal**: Running `npm start` on port 3000

### Workflow

1. Open your browser to `http://localhost:3000`
2. Enter a decision dilemma
3. Adjust agent weights (optional)
4. Click "Start Council Debate"
5. Wait for results (30-60 seconds depending on LLM speed)
6. View recommendations, conflict heatmap, and agent analyses

---

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
# Then update FRONTEND_URL in .env if needed
```

**Module not found error:**
```bash
# Make sure venv is activated, then reinstall
pip install --upgrade -r requirements.txt
```

**Gemini API errors:**
- Verify your API key is correct in `.env`
- Check you have a valid Gemini API key from https://aistudio.google.com/app/apikey

### Frontend Issues

**Port 3000 already in use:**
```bash
# React will ask if you want to use a different port
# Press 'Y' to use 3001
```

**npm modules not installed:**
```bash
# Clear npm cache and reinstall
npm cache clean --force
npm install
```

**Backend not responding:**
- Check that backend terminal shows `Uvicorn running on http://127.0.0.1:8000`
- Check network tab in browser DevTools (F12) for CORS errors

---

## Building for Production

### Backend

```bash
# No build needed for FastAPI, deploy the folder as-is
# Or build Docker image (requires Docker Desktop)
```

### Frontend

```bash
cd frontend
npm run build
```

This creates an optimized production build in `frontend/build/`.

Deploy the `build` folder to Vercel, Netlify, or any static host.

---

## Stopping the Application

In each terminal window:

```bash
Ctrl + C
```

To deactivate the Python virtual environment:

```bash
deactivate
```

---

## File Structure

```
synapse-council/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── schemas.py
│   │   ├── llm_client.py
│   │   ├── orchestrator.py
│   │   ├── agents/
│   │   │   ├── base.py
│   │   │   ├── risk_logic.py
│   │   │   ├── eq_advocate.py
│   │   │   ├── values_guard.py
│   │   │   └── red_team.py
│   ├── .env
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DecisionInput.tsx
│   │   │   ├── ResultsPanel.tsx
│   │   │   ├── ConflictHeatmap.tsx
│   │   │   ├── AgentCard.tsx
│   │   │   └── LoadingSpinner.tsx
│   │   ├── styles/
│   │   │   ├── DecisionInput.css
│   │   │   ├── ResultsPanel.css
│   │   │   ├── ConflictHeatmap.css
│   │   │   ├── AgentCard.css
│   │   │   └── LoadingSpinner.css
│   │   ├── App.tsx
│   │   ├── index.tsx
│   │   ├── types.ts
│   │   ├── api.ts
│   │   └── index.css
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   └── tsconfig.json
└── WINDOWS_SETUP.md
```

---

## Need Help?

1. Check console errors in browser (F12 → Console tab)
2. Check backend terminal for error messages
3. Verify all dependencies are installed:
   - Backend: `pip list`
   - Frontend: `npm list`
4. Ensure `.env` file is in `backend/` folder with valid API key

---

Happy deciding! 🎯