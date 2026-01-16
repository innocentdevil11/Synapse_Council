import json
import logging
from typing import Type, TypeVar
import warnings
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """
    Legacy wrapper for Google Gemini API.
    DEPRECATED: Use OllamaClient instead for free local LLM.
    
    This class is kept for backward compatibility only.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7,
        max_tokens: int = 1500,
    ):
        warnings.warn(
            "LLMClient (Gemini) is deprecated. Use OllamaClient for free local LLM instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "google.generativeai not installed. "
                "Please use OllamaClient instead or install: pip install google-generativeai"
            )
        
        genai.configure(api_key=api_key)
        self.model_name = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def call_with_schema(
        self,
        system_prompt: str,
        user_message: str,
        response_model: Type[T],
    ) -> T:
        """
        Call Gemini with JSON output.
        Returns a parsed Pydantic model instance.
        DEPRECATED: Use OllamaClient instead.
        """
        raise NotImplementedError(
            "LLMClient is deprecated. Please use OllamaClient for free local LLM. "
            "Update your .env to set LLM_PROVIDER=ollama"
        )

    async def call_plain(self, system_prompt: str, user_message: str) -> str:
        """
        Call Gemini without structured output. Returns raw string response.
        DEPRECATED: Use OllamaClient instead.
        """
        raise NotImplementedError(
            "LLMClient is deprecated. Please use OllamaClient for free local LLM. "
            "Update your .env to set LLM_PROVIDER=ollama"
        )

# Comet Code

# import json
# import logging
# from typing import Type, TypeVar, TypeAlias, Any, Dict, List

# import httpx
# from pydantic import BaseModel

# logger = logging.getLogger(__name__)

# T = TypeVar("T", bound=BaseModel)

# BASE_URL = "https://api.on-demand.io/chat/v1"


# class LLMClient:
#     """
#     LLM wrapper for On‑Demand GPT‑5.x / GPT‑4o endpoint.

#     Usage:
#         client = LLMClient(api_key="Qb94qMlV3RbnYSdf7XhdOlHYhSNvBeWe", endpoint_id="predefined-openai-gpt4o")
#         result: MySchema = await client.call_with_schema(system_prompt, user_message, MySchema)
#         text: str = await client.call_plain(system_prompt, user_message)
#     """

#     def __init__(
#         self,
#         api_key: str,
#         endpoint_id: str = "predefined-openai-gpt4o",
#         agent_ids: List[str] | None = None,
#         reasoning_mode: str = "gpt-5.2",
#         temperature: float = 0.7,
#         max_tokens: int = 1500,
#         top_p: float = 1.0,
#         presence_penalty: float = 0.0,
#         frequency_penalty: float = 0.0,
#     ):
#         self.api_key = api_key
#         self.endpoint_id = endpoint_id
#         # You can override per-call; this is a default
#         self.agent_ids = agent_ids or []
#         self.reasoning_mode = reasoning_mode
#         self.temperature = temperature
#         self.max_tokens = max_tokens
#         self.top_p = top_p
#         self.presence_penalty = presence_penalty
#         self.frequency_penalty = frequency_penalty

#     async def _create_session(self, agent_ids: List[str]) -> str:
#         """Create a chat session and return its ID."""
#         url = f"{BASE_URL}/sessions"
#         body: Dict[str, Any] = {
#             "agentIds": agent_ids,
#             # externalUserId/contextMetadata optional; omit for now
#         }
#         headers = {
#             "apikey": self.api_key,
#             "Content-Type": "application/json",
#         }

#         async with httpx.AsyncClient(timeout=60) as client:
#             resp = await client.post(url, json=body, headers=headers)
#         if resp.status_code != 201:
#             logger.error("Error creating On‑Demand session: %s - %s", resp.status_code, resp.text)
#             raise RuntimeError(f"On‑Demand session error: {resp.status_code}")
#         data = resp.json()["data"]
#         return data["id"]

#     async def _query(
#         self,
#         query: str,
#         agent_ids: List[str],
#         response_mode: str = "sync",
#         reasoning_mode: str | None = None,
#     ) -> Dict[str, Any]:
#         """
#         Low-level call to /sessions/{id}/query, returns parsed JSON dict.
#         """
#         if not agent_ids:
#             agent_ids = self.agent_ids
#         if not agent_ids:
#             raise ValueError("No agent_ids provided for On‑Demand query")

#         session_id = await self._create_session(agent_ids)
#         url = f"{BASE_URL}/sessions/{session_id}/query"

#         body: Dict[str, Any] = {
#             "endpointId": self.endpoint_id,
#             "query": query,
#             "agentIds": agent_ids,
#             "responseMode": response_mode,
#             "reasoningMode": reasoning_mode or self.reasoning_mode,
#             "modelConfigs": {
#                 "fulfillmentPrompt": "",
#                 "stopSequences": [],
#                 "temperature": self.temperature,
#                 "topP": self.top_p,
#                 "maxTokens": self.max_tokens,
#                 "presencePenalty": self.presence_penalty,
#                 "frequencyPenalty": self.frequency_penalty,
#             },
#         }

#         headers = {
#             "apikey": self.api_key,
#             "Content-Type": "application/json",
#         }

#         async with httpx.AsyncClient(timeout=None) as client:
#             resp = await client.post(url, json=body, headers=headers)

#         if resp.status_code != 200:
#             logger.error("On‑Demand query error: %s - %s", resp.status_code, resp.text)
#             raise RuntimeError(f"On‑Demand query error: {resp.status_code}")

#         return resp.json()

#     async def call_plain(
#         self,
#         system_prompt: str,
#         user_message: str,
#         agent_ids: List[str] | None = None,
#     ) -> str:
#         """
#         Call On‑Demand without structured parsing.
#         Returns raw answer string (or entire JSON if 'answer' field missing).
#         """
#         prompt = f"{system_prompt}\n\nUser:\n{user_message}"
#         data = await self._query(prompt, agent_ids or self.agent_ids)

#         # Adjust this depending on actual response shape from your account.
#         if "data" in data and "answer" in data["data"]:
#             return data["data"]["answer"]
#         return json.dumps(data)

#     async def call_with_schema(
#         self,
#         system_prompt: str,
#         user_message: str,
#         response_model: Type[T],
#         agent_ids: List[str] | None = None,
#     ) -> T:
#         """
#         Call On‑Demand and parse the result as JSON into a Pydantic model.

#         Your system_prompt MUST instruct the model to return STRICT JSON
#         that matches the schema of `response_model`.
#         """
#         prompt = (
#             f"{system_prompt}\n\n"
#             f"User:\n{user_message}\n\n"
#             "Return ONLY a single JSON object that matches the expected schema."
#         )
#         data = await self._query(prompt, agent_ids or self.agent_ids)

#         # Try to extract the JSON text from 'answer', then parse.
#         if "data" in data and "answer" in data["data"]:
#             raw_answer = data["data"]["answer"]
#         else:
#             # Fallback: treat entire response as JSON string
#             raw_answer = json.dumps(data)

#         try:
#             parsed = json.loads(raw_answer)
#         except json.JSONDecodeError:
#             logger.error("Failed to parse JSON from On‑Demand answer: %s", raw_answer[:500])
#             raise

#         return response_model.model_validate(parsed)



# tanishq code


# services/ondemand_client.py









# import os
# import requests
# from dotenv import load_dotenv

# load_dotenv()

# ONDEMAND_API_KEY = os.getenv("ONDEMAND_API_KEY")

# API_URL = "https://api.on-demand.io/chat/v1/sessions/query"

# HEADERS = {
#     "apikey": ONDEMAND_API_KEY,
#     "Content-Type": "application/json"
# }

# # This endpointId comes from your curl example
# DEFAULT_ENDPOINT = "predefined-openai-gpt4.1-nano"


# def chat(query: str, endpoint_id: str = DEFAULT_ENDPOINT):
#     payload = {
#         "query": query,
#         "endpointId": endpoint_id,
#         "responseMode": "sync"
#     }

#     response = requests.post(API_URL, headers=HEADERS, json=payload)

#     if response.status_code != 200:
#         print("Status:", response.status_code)
#         print("Response:", response.text)
#         raise Exception("OnDemand Chat API failed")

#     data = response.json()

#     # OnDemand usually returns output inside this structure
#     if "data" in data and "answer" in data["data"]:
#         return data["data"]["answer"]

#     # fallback
#     return data


# # ---------------- TEST ----------------

# if __name__ == "__main__":
#     reply = chat("What is 2 + 2?")
#     print("API RESPONSE:\n", reply)


