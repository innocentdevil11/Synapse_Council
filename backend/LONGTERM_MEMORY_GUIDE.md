# 📝 Long-Term Memory & Conflict Analyzer Bypass - Implementation

## Changes Made

### 1. Configuration Updates

#### `.env.example` - Updated
- **Removed**: `ON_DEMAND_CONFLICT_AGENT=conflict-analyzer` (tool doesn't exist)
- **Added**: Long-term memory configuration
  ```env
  ENABLE_LONG_TERM_MEMORY=true
  LONG_TERM_MEMORY_TYPE=ondemand
  ON_DEMAND_MEMORY_AGENT=tool-1717503940
  ```

#### `app/config.py` - Updated
- Removed `ON_DEMAND_CONFLICT_AGENT` configuration
- Added `ENABLE_LONG_TERM_MEMORY` (bool, default: true)
- Added `LONG_TERM_MEMORY_TYPE` (str, default: "ondemand")
- Added `ON_DEMAND_MEMORY_AGENT` (uses GPT agent for memory)

### 2. Long-Term Memory in OnDemandClient

#### `app/ondemand_client.py` - Enhanced
Added three new methods:

**1. `__init__()` parameter**
```python
enable_memory: bool = True  # Enable/disable memory features
```

**2. `store_memory()` method** - Persist chat/decisions
```python
async def store_memory(
    session_id: str,
    content: str,
    memory_type: str = "decision",  # "decision", "conversation", "insight"
    metadata: Optional[Dict[str, Any]] = None,
) -> str
```
- Stores conversations, decisions, and insights
- Can be retrieved later for context
- Includes metadata for rich searching

**3. `retrieve_memory()` method** - Fetch stored memories
```python
async def retrieve_memory(
    session_id: str,
    memory_type: Optional[str] = None,
    query_text: Optional[str] = None,
) -> str
```
- Retrieves memories by type or search query
- Returns formatted context for chat
- Returns empty string if memory disabled

### 3. Counsellor Chat Integration

#### `app/counsellor.py` - Updated
Enhanced initialization:
```python
def __init__(self):
    self.client = OnDemandClient(
        api_key=settings.ON_DEMAND_API_KEY,
        enable_memory=settings.ENABLE_LONG_TERM_MEMORY,  # NEW
    )
    self.memory_agent = settings.ON_DEMAND_MEMORY_AGENT  # NEW
    self.enable_ltm = settings.ENABLE_LONG_TERM_MEMORY  # NEW
```

Enhanced chat method:
```python
async def chat(self, session_id: str, message: str, ...):
    # 1. Get local session memory
    memory_summary = await self.memory_manager.get_session_summary(session_id)
    
    # 2. Retrieve long-term memory (NEW)
    ltm_context = await self.client.retrieve_memory(
        session_id=session_id,
        query_text=message,
    )
    
    # 3. Build prompt with both contexts
    full_query = f"{system_prompt}\n\nLong-term context:\n{ltm_context}\n\nUser: {message}"
    
    # 4. Get response
    reply = await self.client.chat(query=full_query, ...)
    
    # 5. Store in long-term memory (NEW)
    await self.client.store_memory(
        session_id=session_id,
        content=f"User: {message}\n\nCounsellor: {reply}",
        memory_type="conversation",
        metadata={"timestamp": ...},
    )
```

### 4. Conflict Analyzer Bypass

#### Solution Approach
Since the conflict analyzer tool doesn't exist on On-Demand, the system now:

1. **Uses GPT agent** instead of separate conflict analyzer
2. **No separate conflict resolution** - conflicts resolved during debate
3. **Conflict analysis** happens through:
   - Head Council synthesis
   - Agent debate framework
   - Multi-perspective analysis

#### Changes in `app/ondemand_client.py`
Updated docstring for `analyze_decision_conflict()`:
```python
async def analyze_decision_conflict(
    self,
    dilemma: str,
    perspectives: List[str],
    model_config: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Use on-demand to analyze decision conflicts and propose resolutions.
    Conflict analysis is handled by GPT agent (no separate conflict analyzer).
    """
```

---

## Feature Details

### Long-Term Memory System

#### What Gets Stored?
- Conversations (queries and responses)
- Decisions made and reasoning
- Insights and lessons learned
- Session metadata and timestamps

#### How Storage Works?
1. User sends message to counsellor
2. Message + counsellor response automatically stored
3. Can be retrieved with optional search filters
4. Persists across sessions

#### How Retrieval Works?
1. User sends new message to counsellor
2. System retrieves relevant past memories
3. Long-term context added to prompt
4. Counsellor aware of past discussions
5. Response uses historical context

#### Benefits
✅ **Continuity** - Remembers past discussions
✅ **Context** - Provides relevant history
✅ **Growth** - Shows decision patterns over time
✅ **Personalization** - Tailored to user's history

### Configuration Options

```env
# Enable/disable long-term memory
ENABLE_LONG_TERM_MEMORY=true

# Where to store memory
LONG_TERM_MEMORY_TYPE=ondemand

# Which agent handles memory
ON_DEMAND_MEMORY_AGENT=tool-1717503940
```

---

## Conflict Handling (Revised)

### What Changed?
- **Before**: Separate conflict analyzer tool
- **After**: GPT agent handles conflict analysis

### How It Works Now
1. Agents provide perspectives (Risk, EQ, Values, Red Team, Gita)
2. Head Council synthesizes viewpoints
3. GPT identifies conflicts via `analyze_decision_conflict()`
4. Debate happens if conflicts exceed threshold
5. Final resolution from multi-perspective synthesis

### No Breaking Changes
✅ Same API endpoints
✅ Same debate framework
✅ Same agent perspectives
✅ Just different conflict handling backend

---

## API Usage Examples

### Store Memory
```python
await counsellor.client.store_memory(
    session_id="user-123",
    content="User decided to change careers after 10 years in finance",
    memory_type="decision",
    metadata={"category": "career", "risk_level": "high"}
)
```

### Retrieve Memory
```python
ltm = await counsellor.client.retrieve_memory(
    session_id="user-123",
    memory_type="decision",
    query_text="career change"
)
# Returns: Previous discussions about career changes
```

### Automatic Storage (In Chat)
```python
# When you call counsellor.chat(), it automatically:
# 1. Retrieves relevant memories
# 2. Uses them in prompt
# 3. Stores new conversation
# No explicit calls needed!
```

---

## Configuration Reference

### Required (.env)
```env
LLM_PROVIDER=ondemand
ON_DEMAND_API_KEY=your_key_here
```

### Optional Long-Term Memory (.env)
```env
ENABLE_LONG_TERM_MEMORY=true
LONG_TERM_MEMORY_TYPE=ondemand
ON_DEMAND_MEMORY_AGENT=tool-1717503940
```

### Removed
```env
# No longer needed:
ON_DEMAND_CONFLICT_AGENT=conflict-analyzer  # ❌ Removed
```

---

## Testing the Implementation

### Test Long-Term Memory Storage
```bash
curl -X POST http://localhost:8000/api/counsellor/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
    "message": "I am considering a major life change"
  }'
```

Then in a new request:
```bash
curl -X POST http://localhost:8000/api/counsellor/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
    "message": "How does this relate to my previous consideration?"
  }'
```

Expected: Counsellor references first conversation in second response

### Test Conflict Analysis
```bash
curl -X POST http://localhost:8000/api/decide \
  -H "Content-Type: application/json" \
  -d '{
    "dilemma": "Accept new job or stay safe?",
    "context": "Job offers different salary but risky startup"
  }'
```

Expected: GPT provides conflict analysis, not separate tool

---

## Files Modified Summary

```
✅ .env.example
   - Removed: ON_DEMAND_CONFLICT_AGENT
   - Added: ENABLE_LONG_TERM_MEMORY
   - Added: ON_DEMAND_MEMORY_AGENT

✅ app/config.py
   - Removed: ON_DEMAND_CONFLICT_AGENT
   - Added: ENABLE_LONG_TERM_MEMORY (bool)
   - Added: LONG_TERM_MEMORY_TYPE (str)
   - Added: ON_DEMAND_MEMORY_AGENT (str)

✅ app/ondemand_client.py
   - Updated: __init__() with enable_memory parameter
   - Added: store_memory() method
   - Added: retrieve_memory() method
   - Updated: analyze_decision_conflict() docstring

✅ app/counsellor.py
   - Updated: __init__() with memory settings
   - Updated: chat() to retrieve and store LTM
   - Added: Long-term memory retrieval before chat
   - Added: Automatic storage after chat response
```

---

## Status

✅ **Long-Term Memory**: Implemented and integrated
✅ **Conflict Analyzer Bypass**: Implemented (uses GPT instead)
✅ **Configuration**: Updated and flexible
✅ **Chat Integration**: Automatic memory management
✅ **Backward Compatible**: No breaking changes

---

## Next Steps

1. Verify `.env` is configured with memory settings
2. Start backend: `uvicorn app.main:app --reload`
3. Test counsellor chat (memory automatic)
4. Test decision endpoint (conflict handled by GPT)
5. Monitor logs for memory operations

---

## Troubleshooting

### Memory Not Being Retrieved
- Check: `ENABLE_LONG_TERM_MEMORY=true` in `.env`
- Check logs for memory retrieval errors
- Verify `ON_DEMAND_MEMORY_AGENT` is valid

### Conflict Analysis Not Working
- Conflict resolved through debate system
- Check Head Council response in `/api/decide`
- GPT handles perspective synthesis

### Memory Storage Errors
- Might fail silently if On-Demand API unavailable
- Check backend logs: `--log-level debug`
- Verify API key validity

---

**Implementation Complete** ✅
Long-term memory is now integrated and conflict analyzer is bypassed with GPT handling.
