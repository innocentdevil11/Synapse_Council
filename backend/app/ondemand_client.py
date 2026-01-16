"""
On-Demand Platform Client
Unified interface for accessing multiple AI tools through on-demand.io:
- GPT-4o / GPT-5.x for text reasoning
- Image analysis (vision)
- Audio transcription
- Bhagavad Gita wisdom agent
- Long-term memory for chat retrieval and storage
- Custom agents for specialized tasks
"""

import json
import logging
from typing import Dict, Any, List, Optional, Type
import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# On-Demand API Configuration
BASE_URL = "https://api.on-demand.io"


class OnDemandClient:
    """
    Client for On-Demand API supporting multiple AI tools and agents.
    Includes long-term memory support for persistent chat retrieval and storage.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = BASE_URL,
        timeout: float = 60.0,
        enable_memory: bool = True,
    ):
        """
        Initialize On-Demand client.
        
        Args:
            api_key: Your on-demand.io API key
            base_url: Base URL for on-demand API
            timeout: Request timeout in seconds
            enable_memory: Enable long-term memory feature
        """
        if not api_key or not api_key.strip():
            raise ValueError("API key is required for On-Demand client")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.enable_memory = enable_memory
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json",
        }

    async def _create_session(
        self,
        agent_ids: List[str],
        context_metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a new chat session.
        
        Args:
            agent_ids: List of agent IDs to use in session
            context_metadata: Optional metadata for the session
            
        Returns:
            Session ID
        """
        url = f"{self.base_url}/chat/v1/sessions"
        body = {
            "agentIds": agent_ids,
        }
        if context_metadata:
            body["contextMetadata"] = context_metadata

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=body, headers=self.headers)

        if response.status_code != 201:
            logger.error(
                f"Error creating on-demand session: {response.status_code} - {response.text}"
            )
            raise RuntimeError(f"On-Demand session creation failed: {response.status_code}")

        data = response.json()
        return data.get("data", {}).get("id")

    async def _query_session(
        self,
        session_id: str,
        query: str,
        agent_ids: List[str],
        endpoint_id: str = "predefined-openai-gpt4o",
        response_mode: str = "sync",
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Query a session.
        
        Args:
            session_id: Session ID to query
            query: User query/prompt
            agent_ids: List of agent IDs
            endpoint_id: Endpoint ID (e.g., "predefined-openai-gpt4o")
            response_mode: "sync" or "async"
            model_config: Model configuration (temperature, max_tokens, etc.)
            
        Returns:
            Response data from on-demand
        """
        url = f"{self.base_url}/chat/v1/sessions/{session_id}/query"

        if model_config is None:
            model_config = {}

        body = {
            "endpointId": endpoint_id,
            "query": query,
            "agentIds": agent_ids,
            "responseMode": response_mode,
            "modelConfigs": {
                "temperature": model_config.get("temperature", 0.7),
                "topP": model_config.get("top_p", 1.0),
                "maxTokens": model_config.get("max_tokens", 1500),
                "presencePenalty": model_config.get("presence_penalty", 0.0),
                "frequencyPenalty": model_config.get("frequency_penalty", 0.0),
            },
        }

        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.post(url, json=body, headers=self.headers)

        if response.status_code != 200:
            logger.error(
                f"On-Demand query error: {response.status_code} - {response.text}"
            )
            raise RuntimeError(f"On-Demand query failed: {response.status_code}")

        return response.json()

    async def chat(
        self,
        query: str,
        agent_ids: List[str],
        endpoint_id: str = "predefined-openai-gpt4o",
        model_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Simple chat interface - direct API call to on-demand.
        
        Args:
            query: User query
            agent_ids: Agent IDs to use
            endpoint_id: Model endpoint
            model_config: Model configuration
            
        Returns:
            Response text
        """
        try:
            if model_config is None:
                model_config = {}

            # Direct API call - query endpoint
            url = f"{self.base_url}/api/chat"
            body = {
                "query": query,
                "endpointId": endpoint_id,
                "modelConfigs": {
                    "temperature": model_config.get("temperature", 0.7),
                    "topP": model_config.get("top_p", 1.0),
                    "maxTokens": model_config.get("max_tokens", 1500),
                    "presencePenalty": model_config.get("presence_penalty", 0.0),
                    "frequencyPenalty": model_config.get("frequency_penalty", 0.0),
                },
            }

            async with httpx.AsyncClient(timeout=None) as client:
                response = await client.post(url, json=body, headers=self.headers)

            if response.status_code != 200:
                logger.error(
                    f"On-Demand API error: {response.status_code} - {response.text}"
                )
                raise RuntimeError(f"On-Demand API call failed: {response.status_code}")

            response_data = response.json()
            
            # Extract answer
            answer = response_data.get("data", {}).get("answer", "")
            if not answer:
                # Try alternative paths
                answer = response_data.get("answer", "")
                if not answer:
                    answer = response_data.get("response", "")

            return answer

        except Exception as e:
            logger.error(f"Error in on-demand chat: {e}", exc_info=True)
            raise

    async def chat_structured(
        self,
        query: str,
        agent_ids: List[str],
        response_model: Type[BaseModel],
        endpoint_id: str = "predefined-openai-gpt4o",
        model_config: Optional[Dict[str, Any]] = None,
    ) -> BaseModel:
        """
        Chat with structured JSON output.
        
        Args:
            query: User query
            agent_ids: Agent IDs to use
            response_model: Pydantic model for response parsing
            endpoint_id: Model endpoint
            model_config: Model configuration
            
        Returns:
            Parsed response model instance
        """
        response_text = await self.chat(
            query=query,
            agent_ids=agent_ids,
            endpoint_id=endpoint_id,
            model_config=model_config,
        )

        try:
            # Try to parse JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
                return response_model(**data)
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            logger.error(f"Error parsing structured response: {e}")
            raise

    async def transcribe_audio(
        self,
        audio_file_path: str,
        agent_ids: Optional[List[str]] = None,
    ) -> str:
        """
        Transcribe audio using on-demand audio agent.
        Falls back to implementation using an audio transcription agent.
        
        Args:
            audio_file_path: Path to audio file
            agent_ids: Optional specific agent IDs
            
        Returns:
            Transcribed text
        """
        if agent_ids is None:
            agent_ids = ["audio-transcription"]

        try:
            with open(audio_file_path, "rb") as f:
                audio_data = f.read()

            # Create session for audio processing
            session_id = await self._create_session(agent_ids)

            # Send audio for transcription (simplified - actual implementation
            # would depend on on-demand's audio API specifics)
            response_data = await self._query_session(
                session_id=session_id,
                query=f"Transcribe this audio file: {audio_file_path}",
                agent_ids=agent_ids,
            )

            transcript = response_data.get("data", {}).get("answer", "")
            logger.info(f"Audio transcribed: {len(transcript)} chars")
            return transcript

        except Exception as e:
            logger.error(f"Error transcribing audio: {e}", exc_info=True)
            raise

    async def analyze_image(
        self,
        image_file_path: str,
        query: str = "Analyze this image",
        agent_ids: Optional[List[str]] = None,
    ) -> str:
        """
        Analyze image using on-demand vision agent.
        
        Args:
            image_file_path: Path to image file
            query: Question or prompt about the image
            agent_ids: Optional specific agent IDs
            
        Returns:
            Analysis text
        """
        if agent_ids is None:
            agent_ids = ["vision-analyzer"]

        try:
            with open(image_file_path, "rb") as f:
                image_data = f.read()

            # Create session for image processing
            session_id = await self._create_session(agent_ids)

            # Query with image (simplified)
            response_data = await self._query_session(
                session_id=session_id,
                query=f"{query}\n\nImage: {image_file_path}",
                agent_ids=agent_ids,
            )

            analysis = response_data.get("data", {}).get("answer", "")
            logger.info(f"Image analyzed: {len(analysis)} chars")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing image: {e}", exc_info=True)
            raise

    async def get_gita_wisdom(
        self,
        query: str,
        model_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Get wisdom from Bhagavad Gita using specialized agent.
        
        Args:
            query: Question or dilemma
            model_config: Model configuration
            
        Returns:
            Gita-based wisdom response
        """
        gita_prompt = f"""You are the Bhagavad Gita Guide. You provide wisdom from the Bhagavad Gita 
to help with life decisions and dilemmas. Reference relevant verses and teachings.

User's question: {query}

Provide a thoughtful, dharma-aligned response based on Gita teachings."""

        return await self.chat(
            query=gita_prompt,
            agent_ids=["gita-guide"],
            model_config=model_config,
        )

    async def store_memory(
        self,
        session_id: str,
        content: str,
        memory_type: str = "decision",
        metadata: Optional[Dict[str, Any]] = None,
        agent_ids: Optional[List[str]] = None,
    ) -> str:
        """
        Store long-term memory of chat/decision for later retrieval.
        
        Args:
            session_id: Session identifier
            content: Content to store (decision, conversation, etc.)
            memory_type: Type of memory ("decision", "conversation", "insight")
            metadata: Additional metadata
            agent_ids: Optional specific agent IDs
            
        Returns:
            Memory storage confirmation
        """
        if not self.enable_memory:
            logger.warning("Long-term memory is disabled")
            return "Memory storage disabled"
        
        if agent_ids is None:
            agent_ids = ["memory-storage"]
        
        try:
            query = f"""Store this memory for session {session_id}:

Type: {memory_type}
Content: {content}

Metadata: {json.dumps(metadata or {})}

Please store this securely for future retrieval."""

            response = await self.chat(
                query=query,
                agent_ids=agent_ids,
            )
            
            logger.info(f"Memory stored for session {session_id}: {memory_type}")
            return response
            
        except Exception as e:
            logger.error(f"Error storing memory: {e}", exc_info=True)
            raise

    async def retrieve_memory(
        self,
        session_id: str,
        memory_type: Optional[str] = None,
        query_text: Optional[str] = None,
        agent_ids: Optional[List[str]] = None,
    ) -> str:
        """
        Retrieve long-term memory for a session.
        
        Args:
            session_id: Session identifier
            memory_type: Optional memory type filter ("decision", "conversation", "insight")
            query_text: Optional search query
            agent_ids: Optional specific agent IDs
            
        Returns:
            Retrieved memory content
        """
        if not self.enable_memory:
            logger.warning("Long-term memory is disabled")
            return ""
        
        if agent_ids is None:
            agent_ids = ["memory-retrieval"]
        
        try:
            filter_text = f"Type: {memory_type}\n" if memory_type else ""
            search_text = f"Search for: {query_text}\n" if query_text else ""
            
            query = f"""Retrieve long-term memory for session {session_id}:

{filter_text}{search_text}

Please retrieve all relevant memories and provide a comprehensive summary."""

            memory_content = await self.chat(
                query=query,
                agent_ids=agent_ids,
            )
            
            logger.info(f"Memory retrieved for session {session_id}")
            return memory_content
            
        except Exception as e:
            logger.error(f"Error retrieving memory: {e}", exc_info=True)
            return ""

    async def analyze_decision_conflict(
        self,
        dilemma: str,
        perspectives: List[str],
        model_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Use on-demand to analyze decision conflicts and propose resolutions.
        Conflict analysis is handled by GPT agent (no separate conflict analyzer).
        
        Args:
            dilemma: The decision dilemma
            perspectives: Different perspectives on the dilemma
            model_config: Model configuration
            
        Returns:
            Conflict analysis
        """
        perspectives_text = "\n".join([f"- {p}" for p in perspectives])

        query = f"""Analyze this decision conflict:

Dilemma: {dilemma}

Perspectives:
{perspectives_text}

Identify the core conflicts, validate each perspective, and suggest integrated resolutions."""

        return await self.chat(
            query=query,
            agent_ids=["conflict-analyzer"],
            model_config=model_config,
        )
