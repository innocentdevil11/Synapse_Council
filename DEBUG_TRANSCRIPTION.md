# Audio Transcription Debugging Guide

## What Was Fixed

1. **requirements.txt** - Removed duplicate dependencies that could cause conflicts:
   - Removed duplicate `python-multipart` entries
   - Removed duplicate `numpy`, `scipy` entries  
   - Removed conflicting `whisper` package (kept only `openai-whisper`)

2. **Backend Logging** - Added detailed console logging to trace execution:
   - `audio_processor.py`: Logs each step of transcription (loading model, processing audio, returning result)
   - `api.py`: Logs WebSocket transcribe requests and responses
   - Better error messages with full stack traces

3. **Frontend Logging** - Added detailed console logging to the AudioRecorder component:
   - WebSocket connection status
   - Audio data being sent
   - Transcribe request timing
   - Messages received from server
   - Error details

4. **Timeout Fix** - Increased delay before sending transcribe request:
   - **Old**: 500ms (too short for Whisper to initialize)
   - **New**: 2000ms (gives model time to load on first use)

## How to Test the Fix

### Step 1: Restart the Backend
```bash
# Terminal 1 - Stop the old process if still running
# Press Ctrl+C

# Install fresh dependencies
cd backend
pip install -r requirements.txt

# Start the backend server
python api.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Restart the Frontend
```bash
# Terminal 2
cd frontend
npm start
```

### Step 3: Test the Transcription
1. Open browser to `http://localhost:3000`
2. Click "Start Recording"
3. Say something like "Hello world"
4. Click "Stop Recording"
5. Click "Transcribe"
6. **Open Browser Developer Tools** (F12 or Ctrl+Shift+I)
7. Go to **Console** tab
8. Watch the logs appear as transcription happens

## What to Look For in the Console

### Frontend Console (Browser F12)
Look for logs starting with `[AudioRecorder]`:

**Success Case:**
```
[AudioRecorder] Connecting to WebSocket: ws://localhost:8000/ws/transcribe-live
[AudioRecorder] WebSocket connected
[AudioRecorder] Sending audio: 12345 bytes
[AudioRecorder] Sending transcribe request
[AudioRecorder] Received message: {"type":"ack","bytes_received":12345,"total_bytes":12345}
[AudioRecorder] Received message: {"type":"transcription","text":"Hello world","language":"en","cached":false,"error":null}
[AudioRecorder] Transcription received: Hello world
```

**Error Case:**
```
[AudioRecorder] WebSocket error: ...
// OR
[AudioRecorder] Error parsing message: ...
// OR
[AudioRecorder] Transcription timeout - no response after 30 seconds
```

### Backend Console (Terminal)
Look for logs starting with `[AUDIO]` or `[WS-TRANSCRIBE]`:

**Success Case:**
```
[AUDIO] Starting transcription: 12345 bytes, language=en, model=base
[AUDIO] Loading Whisper model: base
[AUDIO] Model loaded successfully
[AUDIO] Starting model.transcribe()...
[AUDIO] Transcription complete
[AUDIO] Result: 'Hello world'
[WS-TRANSCRIBE] Received transcribe request with 12345 bytes
[WS-TRANSCRIBE] Sending result: {'text': 'Hello world', ...}
```

**Error Case:**
```
[AUDIO ERROR] Transcription exception: ...
[WS-TRANSCRIBE-ERROR] Transcription error: ...
```

## First-Time Setup Notes

### On First Run, You'll See:
```
[AUDIO] Loading Whisper model: base
Loading Whisper base model (first load may take a moment)...
```

This downloads the model (~139MB) and may take 30-60 seconds the first time. The browser will show "Transcription timeout" if you only waited 5 seconds. Just wait and try again - **the model gets cached after first download.**

### Model Size Options
If the Whisper model download is too large:
- Current: `base` (139MB, good accuracy)
- Smaller: `tiny` (39MB, less accurate, much faster)
- Larger: `small` (466MB), `medium` (1.5GB), `large` (3.1GB)

To change, edit `api.py` line 232:
```python
# Change from:
result = await transcribe_audio_async(audio_bytes, language)
# To (e.g., for tiny model):
result = await transcribe_audio_async(audio_bytes, language, model_size="tiny")
```

## Network Tab Debugging

If frontend console looks good but you want to verify WebSocket communication:

1. Open **Network** tab in DevTools (F12)
2. Filter by "WS" (WebSocket)
3. Click on the `transcribe-live` connection
4. Click **Messages** sub-tab
5. You should see:
   - **Sent**: `{"type":"audio","data":"[base64...]","language":"en"}`
   - **Received**: `{"type":"ack","bytes_received":...}`
   - **Sent**: `{"type":"transcribe"}`
   - **Received**: `{"type":"transcription","text":"...","language":"en"}`

## Troubleshooting Checklist

- [ ] Ran `pip install -r requirements.txt` in backend folder
- [ ] Backend started without errors (check for `Uvicorn running`)
- [ ] Frontend started without errors (check for `compiled successfully`)
- [ ] Both URLs accessible: `http://localhost:3000` and `http://localhost:8000`
- [ ] Browser console shows `[AudioRecorder]` logs appearing
- [ ] Backend console shows `[AUDIO]` logs appearing
- [ ] Recording starts and stops (microphone access working)
- [ ] Waited at least 2 seconds after stopping recording before transcribe appears

## Still Not Working?

Run this diagnostic check:

**Terminal 3:**
```bash
cd backend
python -c "
import audio_processor
print('Testing Whisper...')
model = audio_processor.get_whisper_model()
print('Model loaded:', model)
"
```

If this hangs or errors, the Whisper model installation has issues.

## Additional Help

- **Whisper not installing?** Make sure you have `torch` installed (required dependency)
- **Out of memory?** The base model needs ~2GB RAM. If your machine is low on memory, use the `tiny` model instead
- **Still timing out?** Increase the timeout on line 2000 in AudioRecorder.jsx from 2000ms to 5000ms or more
- **Port already in use?** Change backend port in api.py line ~480 (search for `port=8000`) or frontend port in next.config.mjs

