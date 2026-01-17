import json
import os
import sys
import uuid
import requests
from typing import List, Dict, Optional

from pathlib import Path
from dotenv import load_dotenv

# ================= ENV SETUP =================

current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
dotenv_path = backend_dir / '.env'

load_dotenv(dotenv_path=dotenv_path)

API_KEY = os.getenv("ONDEMAND_API_KEY")
BASE_URL = "https://api.on-demand.io/chat/v1"
MEDIA_BASE_URL = "https://api.on-demand.io/media/v1"

EXTERNAL_USER_ID = os.getenv("USER_ID")

# QUERY will be dynamically injected (JSON string)
QUERY = ""

RESPONSE_MODE = "sync"
AGENT_IDS = ["agent-1712327325","agent-1713962163"]

ENDPOINT_ID = "predefined-openai-gpt5.2"
REASONING_MODE = "grok-4-fast"

FULFILLMENT_PROMPT = """You are the Final Aggregator Agent in the Synapse Council.

Your task is to produce ONE concise paragraph that resolves the user’s dilemma by
synthesizing all agent outputs using:
(a) user-defined weights for each agent, and
(b) the alignment / risk scores provided by each agent.

Operating Rules:
- Treat user-provided weights as authoritative and apply them strictly.
- Give greater influence to agents with higher weights AND stronger internal scores.
- If a high-weight agent has a low alignment score or high risk score, downgrade confidence accordingly.
- Resolve conflicts by favoring the highest weighted agent unless its score indicates instability.
- Preserve uncertainty honestly if scores or weights strongly disagree.

Computation Guidelines (internal only):
- Influence ∝ (agent_weight × agent_score)
- Normalize influence before synthesizing judgment.
- Do NOT expose calculations or numbers to the user.

Output Constraints:
- Exactly one paragraph
- 3–5 sentences
- Clear recommended action
- At most one key reason and one key caveat

You are NOT allowed to:
- Mention agents, weights, or scores explicitly
- Show analysis, math, or debate
- Present multiple options

Purpose:
Transform weighted, scored deliberation into a clear and actionable decision.
"""

STOP_SEQUENCES = []
TEMPERATURE = 0.7
TOP_P = 1
MAX_TOKENS = 873
PRESENCE_PENALTY = 0
FREQUENCY_PENALTY = 0

# ================= DATA CLASSES =================

class ContextField:
    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value

class SessionData:
    def __init__(self, id: str, context_metadata: List[ContextField]):
        self.id = id
        self.context_metadata = context_metadata

class CreateSessionResponse:
    def __init__(self, data: SessionData):
        self.data = data

# ================= CORE FUNCTIONS (UNCHANGED) =================

def create_chat_session(context_metadata: List[Dict[str, str]]) -> str:
    url = BASE_URL + "/sessions"

    body = {
        "agentIds": AGENT_IDS,
        "externalUserId": EXTERNAL_USER_ID,
        "contextMetadata": context_metadata,
    }

    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=body, headers=headers)

    if response.status_code == 201:
        return response.json()["data"]["id"]

    raise RuntimeError("Failed to create chat session")

# ================= RETURN-BASED QUERY (ADDED) =================

def submit_query_and_return(session_id: str, context_metadata: List[Dict[str, str]]) -> str:
    url = f"{BASE_URL}/sessions/{session_id}/query"

    body = {
        "endpointId": ENDPOINT_ID,
        "query": QUERY,
        "agentIds": AGENT_IDS,
        "responseMode": "sync",
        "reasoningMode": REASONING_MODE,
        "modelConfigs": {
            "fulfillmentPrompt": FULFILLMENT_PROMPT,
            "stopSequences": STOP_SEQUENCES,
            "temperature": TEMPERATURE,
            "topP": TOP_P,
            "maxTokens": MAX_TOKENS,
            "presencePenalty": PRESENCE_PENALTY,
            "frequencyPenalty": FREQUENCY_PENALTY,
        },
    }

    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=body, headers=headers)
    response.raise_for_status()

    return response.json()["data"]["answer"]

# ================= LANGGRAPH-CALLABLE WRAPPER =================

def run_aggregator_agent(payload: Dict) -> str:
    """
    payload schema (expected):
    {
      "user_query": str,
      "weights": { agent_name: float },
      "agent_outputs": {
          agent_name: {
              "output": str,
              "score": float
          }
      }
    }
    """
    global QUERY, EXTERNAL_USER_ID

    # Serialize structured payload into the query
    QUERY = json.dumps(payload, indent=2)

    if not EXTERNAL_USER_ID:
        EXTERNAL_USER_ID = str(uuid.uuid4())

    context_metadata = [
        {"key": "userId", "value": "1"},
        {"key": "name", "value": "John"},
    ]

    session_id = create_chat_session(context_metadata)
    return submit_query_and_return(session_id, context_metadata)

# ================= STANDALONE EXECUTION =================

def main():
    demo_payload = {
        "user_query": "Should I invest in cryptocurrency?",
        "weights": {
            "ethical": 0.2,
            "risk": 0.3,
            "eq": 0.2,
            "values": 0.2,
            "red_team": 0.1
        },
        "agent_outputs": {}
    }

    print(run_aggregator_agent(demo_payload))

if __name__ == "__main__":
    main()
