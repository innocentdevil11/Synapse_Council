"""
Counsellor Chat Mode: Session-aware conversational interface.
Remembers past decisions and provides continuity across sessions.
Uses On-Demand platform for GPT-based conversations.
"""

import logging
from typing import Tuple, Optional
from app.ondemand_client import OnDemandClient
from app.config import get_settings
from app.memory import MemoryManager, MemoryEntry

logger = logging.getLogger(__name__)


class CounsellorChat:
    """
    Synapse Counsellor: A session-aware chat interface that remembers decisions.
    Uses On-Demand GPT for natural conversation with long-term memory.
    """
    
    def __init__(self):
        self.memory_manager = MemoryManager()
        settings = get_settings()
        
        # Initialize On-Demand client (required)
        if not settings.ON_DEMAND_API_KEY:
            raise ValueError("ON_DEMAND_API_KEY is required for Counsellor Chat")
        
        self.client = OnDemandClient(
            api_key=settings.ON_DEMAND_API_KEY,
            enable_memory=settings.ENABLE_LONG_TERM_MEMORY,
        )
        self.gpt_agent = settings.ON_DEMAND_GPT_AGENT
        self.memory_agent = settings.ON_DEMAND_MEMORY_AGENT
        self.enable_ltm = settings.ENABLE_LONG_TERM_MEMORY
        logger.info("Counsellor initialized with On-Demand client")
        logger.info(f"Long-term memory enabled: {self.enable_ltm}")
    
    def _build_system_prompt(self, session_summary: str) -> str:
        """Build the system prompt with session context."""
        return f"""You are the Synapse Counsellor, a wise and compassionate decision guide.

Your role:
- You remember and build upon previous decisions made in this session
- You blend practical wisdom (risk analysis, emotional intelligence, values alignment) with dharmic/philosophical perspective
- You help the user explore their dilemmas deeply, asking clarifying questions and offering multiple viewpoints
- You reference past decisions when relevant, helping the user see patterns and growth

Session History:
{session_summary}

Guidelines:
- Be warm, empathetic, and non-judgmental
- Encourage deep reflection and self-awareness
- Offer actionable guidance while respecting the user's autonomy
- When appropriate, reference dharma/values-based reasoning (like the Gita) alongside practical considerations
- Keep responses concise but meaningful (2-3 paragraphs typically)

Current conversation:"""
    
    async def chat(
        self,
        session_id: str,
        message: str,
    ) -> Tuple[str, str]:
        """
        Chat with the counsellor in a session using On-Demand.
        
        Args:
            session_id: Unique session identifier
            message: User's message (can be new dilemma or follow-up)
            
        Returns:
            Tuple of (counsellor_reply, session_summary)
        """
        try:
            # Get session memory summary (local)
            memory_summary = await self.memory_manager.get_session_summary(session_id)
            
            # Retrieve long-term memory
            ltm_context = ""
            if self.enable_ltm:
                try:
                    ltm_context = await self.client.retrieve_memory(
                        session_id=session_id,
                        query_text=message,
                    )
                    if ltm_context:
                        logger.info(f"Retrieved long-term memory for session {session_id}")
                except Exception as e:
                    logger.warning(f"Could not retrieve long-term memory: {e}")
            
            # Build system prompt with context
            system_prompt = self._build_system_prompt(memory_summary)
            
            # Combine system prompt and user message
            full_query = f"{system_prompt}\n\nLong-term context:\n{ltm_context}\n\nUser: {message}"
            
            # Call On-Demand GPT (only option)
            reply = await self.client.chat(
                query=full_query,
                agent_ids=[self.gpt_agent],
                model_config={
                    "temperature": 0.7,
                    "max_tokens": 1000,
                },
            )
            
            reply = reply.strip()
            
            # Store interaction in long-term memory
            if self.enable_ltm:
                try:
                    await self.client.store_memory(
                        session_id=session_id,
                        content=f"User: {message}\n\nCounsellor: {reply}",
                        memory_type="conversation",
                        metadata={"timestamp": str(__import__('datetime').datetime.now())},
                    )
                    logger.info(f"Stored conversation in long-term memory for session {session_id}")
                except Exception as e:
                    logger.warning(f"Could not store long-term memory: {e}")
            
            # If the message looks like a new dilemma, optionally save it
            if any(keyword in message.lower() for keyword in ["should i", "dilemma", "decide", "choice"]):
                await self.memory_manager.add_entry(
                    session_id=session_id,
                    dilemma=message[:200],  # Truncate for storage
                    recommendation="(Awaiting council decision)",
                )
            
            logger.info(f"Counsellor replied to session {session_id}: {len(reply)} chars")
            
            return reply, memory_summary
        
        except Exception as e:
            logger.error(f"Error in counsellor chat: {e}", exc_info=True)
            raise
    
    async def save_decision(
        self,
        session_id: str,
        dilemma: str,
        recommendation: str,
        outcome: Optional[str] = None,
    ) -> MemoryEntry:
        """
        Save a council decision to the session memory.
        Called after /api/decide completes.
        """
        entry = await self.memory_manager.add_entry(
            session_id=session_id,
            dilemma=dilemma,
            recommendation=recommendation,
            outcome=outcome,
        )
        
        logger.info(f"Saved decision to session {session_id}")
        return entry
    
    async def get_history(self, session_id: str) -> str:
        """Get a formatted history of the session."""
        return await self.memory_manager.get_session_summary(session_id)
    
    async def clear_history(self, session_id: str) -> bool:
        """Clear a session's history."""
        return await self.memory_manager.clear_session(session_id)