from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict
from contextlib import asynccontextmanager

from graph.graph import build_synapse_council_graph

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
