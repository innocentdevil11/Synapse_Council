from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Optional
from contextlib import asynccontextmanager
import io
import json
import base64
import asyncio

from graph.graph import build_synapse_council_graph
from audio_processor import transcribe_audio_async, get_cache_stats, clear_cache

# Global graph instance
graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize graph at startup"""
    global graph
    graph = build_synapse_council_graph()
    yield
    # Cleanup if needed
    graph = None


app = FastAPI(
    title="Synapse Council API",
    description="Multi-agent decision system API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Models
class Weights(BaseModel):
    ethical: float = Field(..., ge=0.0, le=1.0)
    risk: float = Field(..., ge=0.0, le=1.0)
    eq: float = Field(..., ge=0.0, le=1.0)
    values: float = Field(..., ge=0.0, le=1.0)
    red_team: float = Field(..., ge=0.0, le=1.0)


class DecisionRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)
    weights: Weights


class AgentOutputs(BaseModel):
    ethical: str
    risk: str
    eq: str
    values: str
    red_team: str


class DecisionResponse(BaseModel):
    agent_outputs: AgentOutputs
    final_decision: str


class TranscriptionResponse(BaseModel):
    text: str
    language: Optional[str] = "en"
    cached: bool = False
    error: Optional[str] = None


@app.get("/")
async def root():
    return {
        "message": "Synapse Council API",
        "status": "operational",
        "endpoints": ["/decision"]
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "graph_initialized": graph is not None}


@app.websocket("/ws/transcribe-live")
async def websocket_transcribe(websocket: WebSocket):
    """
    WebSocket endpoint for REAL-TIME live audio transcription.
    
    Live audio streaming without recording/uploading delays!
    
    Protocol:
    1. Client sends base64-encoded audio chunks
    2. Server transcribes each chunk and sends results back
    3. Client can send "END" message to finalize transcription
    
    Example usage (frontend):
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws/transcribe-live');
    ws.onmessage = (event) => {
      const result = JSON.parse(event.data);
      console.log("Transcribed:", result.text);
    };
    // Send audio chunk
    ws.send(JSON.stringify({
      type: "audio",
      data: base64AudioChunk,
      language: "en"
    }));
    ```
    """
    await websocket.accept()
    accumulated_audio = io.BytesIO()
    language = "en"
    
    try:
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "audio":
                    # Accumulate audio data
                    audio_data = base64.b64decode(message.get("data", ""))
                    accumulated_audio.write(audio_data)
                    language = message.get("language", "en")
                    
                    # Send acknowledgment
                    await websocket.send_json({
                        "type": "ack",
                        "bytes_received": len(audio_data),
                        "total_bytes": accumulated_audio.tell()
                    })
                
                elif message.get("type") == "transcribe":
                    # Transcribe accumulated audio
                    audio_bytes = accumulated_audio.getvalue()
                    print(f"[WS-TRANSCRIBE] Received transcribe request with {len(audio_bytes)} bytes")
                    if audio_bytes:
                        try:
                            result = await transcribe_audio_async(audio_bytes, language)
                            print(f"[WS-TRANSCRIBE] Sending result: {result}")
                            await websocket.send_json({
                                "type": "transcription",
                                "text": result.get("text", ""),
                                "language": result.get("language", language),
                                "cached": result.get("cached", False),
                                "error": result.get("error")
                            })
                            # Reset for next stream
                            accumulated_audio = io.BytesIO()
                        except Exception as e:
                            error_msg = f"Transcription error: {str(e)}"
                            print(f"[WS-TRANSCRIBE-ERROR] {error_msg}")
                            await websocket.send_json({
                                "type": "error",
                                "message": error_msg
                            })
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": "No audio data accumulated"
                        })
                
                elif message.get("type") == "END":
                    # Final transcription and close
                    audio_bytes = accumulated_audio.getvalue()
                    if audio_bytes:
                        result = await transcribe_audio_async(audio_bytes, language)
                        await websocket.send_json({
                            "type": "transcription",
                            "text": result.get("text", ""),
                            "language": result.get("language", language),
                            "cached": result.get("cached", False),
                            "final": True,
                            "error": result.get("error")
                        })
                    break
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
                
    except WebSocketDisconnect:
        print("Client disconnected from transcription WebSocket")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Error: {str(e)}"
        })
        await websocket.close(code=1011, reason=str(e))


@app.websocket("/ws/transcribe-and-decide")
async def websocket_transcribe_and_decide(websocket: WebSocket):
    """
    WebSocket endpoint for LIVE AUDIO + REAL-TIME DECISION.
    
    Combines transcription and decision-making in one streaming connection!
    
    Protocol:
    1. Client sends audio chunks
    2. Server transcribes and makes decision
    3. Server streams agent outputs as they complete
    4. Send "DECIDE" message to trigger decision analysis
    """
    await websocket.accept()
    accumulated_audio = io.BytesIO()
    language = "en"
    weights = {
        "ethical": 0.2,
        "risk": 0.2,
        "eq": 0.2,
        "values": 0.2,
        "red_team": 0.2,
    }
    
    try:
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "audio":
                    audio_data = base64.b64decode(message.get("data", ""))
                    accumulated_audio.write(audio_data)
                    language = message.get("language", "en")
                    
                    await websocket.send_json({
                        "type": "ack",
                        "bytes_received": len(audio_data)
                    })
                
                elif message.get("type") == "weights":
                    # Update decision weights
                    weights.update(message.get("weights", {}))
                    await websocket.send_json({
                        "type": "weights_updated",
                        "weights": weights
                    })
                
                elif message.get("type") == "DECIDE":
                    # Transcribe audio
                    audio_bytes = accumulated_audio.getvalue()
                    if not audio_bytes:
                        await websocket.send_json({
                            "type": "error",
                            "message": "No audio data"
                        })
                        break
                    
                    # Transcribe
                    transcription = await transcribe_audio_async(audio_bytes, language)
                    query = transcription.get("text", "")
                    
                    await websocket.send_json({
                        "type": "transcribed",
                        "text": query,
                        "language": transcription.get("language")
                    })
                    
                    if query and graph:
                        try:
                            # Make decision
                            initial_state = {
                                "user_query": query,
                                "weights": weights,
                                "agent_outputs": {},
                                "final_answer": "",
                            }
                            
                            result = graph.invoke(initial_state)
                            
                            # Stream agent outputs
                            for agent, data in result["agent_outputs"].items():
                                await websocket.send_json({
                                    "type": "agent_response",
                                    "agent": agent,
                                    "output": data["output"]
                                })
                            
                            # Final decision
                            await websocket.send_json({
                                "type": "final_decision",
                                "decision": result["final_answer"],
                                "complete": True
                            })
                            
                        except Exception as e:
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Decision error: {str(e)}"
                            })
                    
                    break
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
                
    except WebSocketDisconnect:
        print("Client disconnected from transcribe-and-decide")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })


@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...), language: Optional[str] = None):
    """
    Transcribe audio file to text using OpenAI's Whisper API.
    
    - Supports MP3, MP4, WAV, MPEG, WEBM formats
    - Includes caching for repeated audio
    - Real-time streaming for instant feedback
    - Max file size: 25MB
    
    Args:
        file: Audio file to transcribe
        language: Optional language code (e.g., 'en', 'es', 'fr')
    
    Returns:
        TranscriptionResponse with transcribed text and metadata
    """
    try:
        # Validate file
        if file.size > 25 * 1024 * 1024:  # 25MB limit
            raise HTTPException(status_code=413, detail="File too large (max 25MB)")
        
        # Read audio file
        audio_bytes = await file.read()
        
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Transcribe asynchronously
        result = await transcribe_audio_async(audio_bytes, language)
        
        if "error" in result and result["error"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return TranscriptionResponse(
            text=result["text"],
            language=result.get("language", "en"),
            cached=result.get("cached", False)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@app.post("/transcribe-and-decide")
async def transcribe_and_decide(
    file: UploadFile = File(...),
    weights: Optional[str] = None,
    language: Optional[str] = None
):
    """
    Convenience endpoint: Transcribe audio AND get decision in one call.
    
    Reduces round-trip latency by combining operations.
    
    Args:
        file: Audio file to transcribe
        weights: JSON string with agent weights (optional, uses defaults)
        language: Optional language code
    
    Returns:
        Combined transcription and decision response
    """
    try:
        import json
        
        # Transcribe audio
        audio_bytes = await file.read()
        transcription = await transcribe_audio_async(audio_bytes, language)
        
        if "error" in transcription and transcription["error"]:
            raise HTTPException(status_code=400, detail=transcription["error"])
        
        # Parse weights or use defaults
        default_weights = {
            "ethical": 0.2,
            "risk": 0.2,
            "eq": 0.2,
            "values": 0.2,
            "red_team": 0.2,
        }
        
        try:
            if weights:
                parsed_weights = json.loads(weights)
                default_weights.update(parsed_weights)
        except json.JSONDecodeError:
            pass
        
        # Make decision
        decision_request = DecisionRequest(
            query=transcription["text"],
            weights=Weights(**default_weights)
        )
        
        decision_response = await make_decision(decision_request)
        
        return {
            "transcribed_text": transcription["text"],
            "language": transcription.get("language", "en"),
            "transcription_cached": transcription.get("cached", False),
            "decision": decision_response.dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")


@app.post("/decision", response_model=DecisionResponse)
async def make_decision(request: DecisionRequest):
    """
    Execute the Synapse Council decision process.
    
    Takes a user query and agent weights, runs the LangGraph workflow,
    and returns all agent outputs plus the final aggregated decision.
    """
    if graph is None:
        raise HTTPException(status_code=503, detail="Graph not initialized")
    
    try:
        # Prepare initial state
        initial_state = {
            "user_query": request.query,
            "weights": {
                "ethical": request.weights.ethical,
                "risk": request.weights.risk,
                "eq": request.weights.eq,
                "values": request.weights.values,
                "red_team": request.weights.red_team,
            },
            "agent_outputs": {},
            "final_answer": "",
        }
        
        # Execute graph (black box - no modifications)
        result = graph.invoke(initial_state)
        
        # Extract and format response
        agent_outputs = AgentOutputs(
            ethical=result["agent_outputs"]["ethical"]["output"],
            risk=result["agent_outputs"]["risk"]["output"],
            eq=result["agent_outputs"]["eq"]["output"],
            values=result["agent_outputs"]["values"]["output"],
            red_team=result["agent_outputs"]["red_team"]["output"],
        )
        
        response = DecisionResponse(
            agent_outputs=agent_outputs,
            final_decision=result["final_answer"]
        )
        
        return response
        
    except KeyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Missing expected output from graph: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing decision: {str(e)}"
        )


@app.get("/cache-stats")
async def cache_statistics():
    """Get transcription cache statistics."""
    return get_cache_stats()


@app.delete("/cache")
async def clear_transcription_cache():
    """Clear the transcription cache."""
    clear_cache()
    return {"message": "Cache cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
