# UPDATED: Added on-demand API key support, transcribe, upload-image, counsellor/chat routes, and Head Council integration
import logging
import time
import os
import tempfile
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import get_settings
from app.schemas import DecisionRequest, RecommendationResponse, DecisionWeights
from app.orchestrator import Orchestrator
from app.multimodal import transcribe_voice, analyze_image
from app.translation import translate_to_english
from app.counsellor import CounsellorChat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator: Orchestrator = None
counsellor: CounsellorChat = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    global orchestrator, counsellor
    settings = get_settings()
    
    logger.info(f"Starting Synapse Council")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    
    # Log provider details
    if settings.LLM_PROVIDER == "ondemand":
        logger.info("Using On-Demand platform for ALL AI services")
        logger.info(f"  - GPT Agent: {settings.ON_DEMAND_GPT_AGENT}")
        logger.info(f"  - Gita Agent: {settings.ON_DEMAND_GITA_AGENT}")
        logger.info(f"  - Audio Agent: {settings.ON_DEMAND_AUDIO_AGENT}")
        logger.info(f"  - Vision Agent: {settings.ON_DEMAND_VISION_AGENT}")
    else:
        raise ValueError("LLM_PROVIDER must be 'ondemand' - On-Demand only mode")
    
    try:
        orchestrator = Orchestrator(
            conflict_threshold=settings.CONFLICT_THRESHOLD,
            max_debate_rounds=settings.MAX_DEBATE_ROUNDS,
        )
        
        counsellor = CounsellorChat()
        
        logger.info("Orchestrator and Counsellor initialized successfully with On-Demand")
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        raise
    
    yield
    logger.info("Shutting down Synapse Council")


app = FastAPI(
    title="Synapse Council",
    description="Multi-agent decision copilot with multimodal input and counsellor mode",
    version="2.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Request/Response Models =====
class CounsellorChatRequest(BaseModel):
    session_id: str
    message: str


class EnhancedDecisionRequest(BaseModel):
    dilemma: str
    context: Optional[str] = None
    weights: Optional[DecisionWeights] = None
    gita_weight: Optional[float] = 0.0
    image_summaries: Optional[list[str]] = None
    session_id: Optional[str] = None


# ===== Health Check =====
@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "service": "Synapse Council v2.0"}


# ===== Main Decision Endpoint (Enhanced) =====
@app.post("/api/decide", response_model=RecommendationResponse)
async def decide(request: EnhancedDecisionRequest):
    """
    Main endpoint: analyze a decision dilemma through the council of agents.
    Now supports on-demand API keys, image context, and Gita agent.
    """
    global orchestrator

    if orchestrator is None:
        logger.error("Orchestrator not initialized")
        raise HTTPException(status_code=500, detail="Service not ready")

    start_time = time.time()

    try:
        # Normalize weights
        weights = request.weights.normalize() if request.weights else DecisionWeights()
        
        # Build enriched dilemma
        enriched_dilemma = request.dilemma
        if request.image_summaries:
            enriched_dilemma += "\n\n--- Image Context ---\n" + "\n".join(request.image_summaries)
        
        logger.info(
            f"Decision request: dilemma={enriched_dilemma[:50]}... weights={weights.to_dict()}, gita_weight={request.gita_weight}"
        )

        # Run the decision council
        result = await orchestrator.run(
            dilemma=enriched_dilemma,
            context=request.context,
            weights=weights,
            gita_weight=request.gita_weight or 0.0,
        )

        # Add execution time
        result.execution_time_ms = (time.time() - start_time) * 1000
        
        # Store in counsellor memory if session_id provided
        if request.session_id and counsellor:
            try:
                await counsellor.save_decision(
                    session_id=request.session_id,
                    dilemma=request.dilemma,
                    recommendation=result.recommendation,
                )
            except Exception as e:
                logger.warning(f"Failed to save decision to memory: {e}")
        
        logger.info(
            f"Decision completed in {result.execution_time_ms:.0f}ms, "
            f"rounds={result.debate_rounds}, verdict={result.recommendation}"
        )

        return result

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during decision: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your decision. Please try again.",
        )


# ===== Voice Transcription =====
@app.post("/api/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """
    Transcribe audio file to text using On-Demand platform.
    
    Args:
        file: Audio file (mp3, wav, m4a, etc.)
        
    Returns:
        { "transcript": "..." }
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        try:
            # Transcribe using backend On-Demand API key
            transcript = await transcribe_voice(tmp_path)
            logger.info(f"Transcribed {len(transcript)} chars")
            
            return {"transcript": transcript}
        
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    except ValueError as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected transcription error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to transcribe audio")


# ===== Image Analysis =====
@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...), context: Optional[str] = Form(None)):
    """
    Analyze an image and return a vision summary using On-Demand platform.
    
    Args:
        file: Image file (jpg, png, gif, webp)
        context: Optional context hint
        
    Returns:
        { "image_url": "...", "vision_summary": "..." }
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        try:
            # Analyze image using backend On-Demand API key
            image_url, summary = await analyze_image(tmp_path, context)
            logger.info(f"Analyzed image: {len(summary)} chars summary")
            
            return {"image_url": image_url, "vision_summary": summary}
        
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    except ValueError as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected image analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to analyze image")


# ===== Counsellor Chat Mode =====
@app.post("/api/counsellor/chat")
async def counsellor_chat(request: CounsellorChatRequest):
    """
    Chat with the Synapse Counsellor in a session-aware manner.
    Maintains memory of past dilemmas and decisions using On-Demand platform.
    
    Args:
        session_id: Unique session identifier
        message: User message (can be new dilemma or follow-up question)
        
    Returns:
        { "reply": "...", "memory_summary": "...", "session_id": "..." }
    """
    global counsellor
    
    if not counsellor:
        raise HTTPException(status_code=500, detail="Counsellor not initialized")
    
    try:
        reply, memory_summary = await counsellor.chat(
            session_id=request.session_id,
            message=request.message,
        )
        
        logger.info(f"Counsellor chat reply: {len(reply)} chars")
        
        return {
            "reply": reply,
            "memory_summary": memory_summary,
            "session_id": request.session_id,
        }
    
    except Exception as e:
        logger.error(f"Counsellor chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Counsellor error: {str(e)}")


# ===== Root Endpoint =====
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Synapse Council v2.0",
        "docs": "/docs",
        "health": "/health",
        "api": {
            "decide": "/api/decide (POST)",
            "transcribe": "/api/transcribe (POST)",
            "upload_image": "/api/upload-image (POST)",
            "counsellor_chat": "/api/counsellor/chat (POST)",
        },
    }


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )