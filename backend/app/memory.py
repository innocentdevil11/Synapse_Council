"""
Simple in-memory session management for Counsellor mode.
Stores decision history per session_id.
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class MemoryEntry(BaseModel):
    """A single entry in a session's memory."""
    timestamp: str
    dilemma: str
    recommendation: str
    outcome: Optional[str] = None
    notes: Optional[str] = None


class SessionMemory(BaseModel):
    """Memory for a single session."""
    session_id: str
    created_at: str
    entries: List[MemoryEntry] = []
    total_decisions: int = 0


class MemoryManager:
    """
    Simple in-memory store for session-based decision history.
    In production, this would be backed by Redis or a database.
    """
    
    def __init__(self):
        # session_id -> SessionMemory
        self.sessions: Dict[str, SessionMemory] = {}
        logger.info("MemoryManager initialized (in-memory)")
    
    def get_or_create_session(self, session_id: str) -> SessionMemory:
        """Get existing session or create a new one."""
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionMemory(
                session_id=session_id,
                created_at=datetime.now().isoformat(),
            )
            logger.info(f"Created new session: {session_id}")
        
        return self.sessions[session_id]
    
    async def add_entry(
        self,
        session_id: str,
        dilemma: str,
        recommendation: str,
        outcome: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> MemoryEntry:
        """Add a decision entry to a session."""
        session = self.get_or_create_session(session_id)
        
        entry = MemoryEntry(
            timestamp=datetime.now().isoformat(),
            dilemma=dilemma,
            recommendation=recommendation,
            outcome=outcome,
            notes=notes,
        )
        
        session.entries.append(entry)
        session.total_decisions = len(session.entries)
        
        logger.info(f"Added entry to session {session_id}: {dilemma[:50]}...")
        
        return entry
    
    async def get_session_summary(self, session_id: str) -> str:
        """Get a human-readable summary of the session's history."""
        session = self.get_or_create_session(session_id)
        
        if not session.entries:
            return "No previous decisions in this session."
        
        lines = [f"Session {session_id} - {len(session.entries)} decision(s):"]
        
        for i, entry in enumerate(session.entries[-5:], 1):  # Last 5 entries
            lines.append(
                f"\n{i}. [{entry.timestamp[:10]}] {entry.dilemma[:60]}..."
                f"\n   → Recommendation: {entry.recommendation}"
            )
            if entry.outcome:
                lines.append(f"   → Outcome: {entry.outcome}")
        
        return "\n".join(lines)
    
    async def get_full_history(self, session_id: str) -> List[MemoryEntry]:
        """Get all entries for a session."""
        session = self.get_or_create_session(session_id)
        return session.entries
    
    async def add_outcome(
        self,
        session_id: str,
        entry_index: int,
        outcome: str,
        notes: Optional[str] = None,
    ) -> bool:
        """Update an existing entry with outcome and notes."""
        session = self.get_or_create_session(session_id)
        
        if 0 <= entry_index < len(session.entries):
            session.entries[entry_index].outcome = outcome
            if notes:
                session.entries[entry_index].notes = notes
            logger.info(f"Updated entry {entry_index} in session {session_id} with outcome")
            return True
        
        return False
    
    async def clear_session(self, session_id: str) -> bool:
        """Clear a session's history."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session {session_id}")
            return True
        return False
    
    async def list_sessions(self) -> List[str]:
        """List all active session IDs."""
        return list(self.sessions.keys())