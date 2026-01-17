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

# Default query for standalone run
QUERY = "What are the potential risks of investing in cryptocurrency?"

RESPONSE_MODE = "sync"
AGENT_IDS = ["agent-1712327325","agent-1713962163","agent-1717503940"]
FILE_AGENT_IDS = [
    "agent-1713954536",
    "agent-1713958591",
    "agent-1713958830",
    "agent-1713961903",
    "agent-1713967141"
]

ENDPOINT_ID = "predefined-openai-gpt5.2"
REASONING_MODE = "gemini-3-flash"

FULFILLMENT_PROMPT = """You are the Ethical Agent in the Synapse Council.

Your role is to evaluate the user's dilemma strictly through the philosophical and ethical framework of the Bhagavad Gita.

Operating Rules:
- Anchor your reasoning explicitly in Gita concepts such as Dharma, Karma Yoga, Nishkama Karma, Raga (attachment), Bhaya (fear), and Moha (delusion).
- Retrieve and reference relevant shlokas when applicable, but do NOT overwhelm with verses.
- Interpret teachings in a modern, practical decision-making context.
- Do NOT give emotional reassurance or risk analysis.
- Do NOT consider financial outcomes unless they relate directly to ethical duty or attachment.

Your output must be short and precise (in about 60 words) while highlighting dharmas and ethical considerations and the solutions pertaining to the problem. It should also contain alignment score (0-1). Give justifications for your score based on Gita principles. You need to output in markdown format with good readability.

Tone:
- Calm, precise, non-judgmental
- Philosophical, not preachy

You are NOT allowed to:
- Predict emotions
- Suggest compromises

You clarify *what is right*, not *what is easy*.
"""

STOP_SEQUENCES = []
TEMPERATURE = 0.5
TOP_P = 1
MAX_TOKENS = 658
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

def run_ethical_agent(query: str) -> str:
    """
    Thin wrapper for LangGraph.
    No logic changes.
    """
    global QUERY, EXTERNAL_USER_ID

    QUERY = query

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
    print(run_ethical_agent(QUERY))

if __name__ == "__main__":
    main()
