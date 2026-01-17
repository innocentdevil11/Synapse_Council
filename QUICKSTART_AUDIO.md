# 🎤 Quick Start: Live Audio in 3 Minutes

## Install (1 minute)

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies  
cd ../frontend
npm install
```

## Run (30 seconds)

**Terminal 1 - Backend:**
```bash
cd backend
python api.py
# ✅ Server running at http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# ✅ UI running at http://localhost:3000
```

## Use (1 minute)

Go to http://localhost:3000

### Try This:
1. **Click** 🔴 "Start Recording"
2. **Say** "Should I leave my current job to start a startup?"
3. **Click** ⏹️ "Stop Recording"
4. **Click** 🧠 "Transcribe & Decide"
5. **Watch** agents respond in real-time ✨

That's it! No API keys, no uploads, no waiting.

---

## What You Get

✅ **Live Speech-to-Text** (completely free)  
✅ **Real-time Decisions** (agents respond as they analyze)  
✅ **Zero API Costs** (runs locally)  
✅ **Low Latency** (WebSocket streaming)  

---

## First Run Note

When you first start the backend, it downloads the Whisper model (~140MB):
- Takes 1-2 minutes
- Downloaded once, cached forever
- Subsequent runs are fast ⚡

---

## Buttons Explained

| Button | What it does |
|--------|-------------|
| 🔴 Start Recording | Begins capturing audio from your mic |
| ⏹️ Stop Recording | Stops recording |
| ✨ Transcribe | Just convert speech to text |
| 🧠 Transcribe & Decide | Speech → text → AI decision (fastest!) |
| 🗑️ Clear | Reset recording |

---

## Pro Tips

🎧 **Use Headphones** - Avoids echo, improves accuracy  
📢 **Speak Clearly** - Natural speaking speed works great  
🔇 **Quiet Space** - Helps recognition, not required  
⚙️ **Adjust Weights** - Set before recording for custom decisions  

---

## Troubleshooting

**"Permission denied" on microphone?**
→ Allow microphone in browser settings

**"Cannot connect to WebSocket"?**
→ Make sure backend is running (`python api.py`)

**Slow transcription?**
→ First run downloads model. Next runs are faster.

**Poor accuracy?**
→ Speak clearly, minimize background noise

---

## Files Modified

- ✅ `backend/audio_processor.py` - Local Whisper (free)
- ✅ `backend/api.py` - WebSocket endpoints
- ✅ `backend/requirements.txt` - New dependencies
- ✅ `frontend/src/components/AudioRecorder.jsx` - Audio UI
- ✅ `frontend/src/app/page.jsx` - Integration

---

## Before vs After

| Before | After |
|--------|-------|
| Type text only | 🎤 Speak your question |
| Manual upload | Auto-stream audio |
| $0.006/min costs | FREE ✓ |
| High latency | Real-time ✓ |

---

## Next Steps

- 📖 Read [LIVE_AUDIO_SETUP.md](LIVE_AUDIO_SETUP.md) for full docs
- 🔧 Read [AUDIO_CHANGES.md](AUDIO_CHANGES.md) for technical details
- 🚀 Deploy to production with your new voice features!

---

**Enjoy your FREE, instant, voice-powered AI council!** 🎤✨
