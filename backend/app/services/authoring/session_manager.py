"""
Chat Session Management for Authoring Service

Handles:
- Session creation and retrieval
- Session updates
- Message history management
"""

import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from .exceptions import AuthoringServiceError

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages chat sessions for authoring operations.

    In production, this should use Redis for distributed session storage.
    """

    # In-memory storage (should be Redis in production)
    _sessions: Dict[str, Dict] = {}

    @classmethod
    def get_or_create_session(cls, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get existing session or create new one.

        Args:
            session_id: Optional existing session ID

        Returns:
            Session dict with metadata and message history
        """
        if session_id and session_id in cls._sessions:
            return cls._sessions[session_id]

        new_session_id = session_id or str(uuid.uuid4())
        session = {
            'session_id': new_session_id,
            'created_at': datetime.utcnow().isoformat(),
            'messages': [],
            'context_type': None,
            'context_id': None,
            'course_id': None,
            'generated_content': None,
            'file_context': []
        }
        cls._sessions[new_session_id] = session
        return session

    @classmethod
    def get_session(cls, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session dict or None if not found
        """
        return cls._sessions.get(session_id)

    @classmethod
    def update_session(cls, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update session data.

        Args:
            session_id: Session identifier
            updates: Dict of updates to apply

        Returns:
            Updated session dict

        Raises:
            AuthoringServiceError: If session not found
        """
        if session_id not in cls._sessions:
            raise AuthoringServiceError(f"Session not found: {session_id}")

        session = cls._sessions[session_id]
        session.update(updates)
        return session

    @classmethod
    def add_message(
        cls,
        session_id: str,
        role: str,
        content: str,
        generated_content: Optional[Dict] = None
    ) -> None:
        """
        Add message to session history.

        Args:
            session_id: Session identifier
            role: Message role (user or assistant)
            content: Message content
            generated_content: Optional generated content data
        """
        session = cls.get_session(session_id)
        if not session:
            raise AuthoringServiceError(f"Session not found: {session_id}")

        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat()
        }

        if generated_content is not None:
            message['generated_content'] = generated_content is not None

        session['messages'].append(message)

    @classmethod
    def get_conversation_history(cls, session_id: str, limit: int = 10) -> list:
        """
        Get conversation history for session.

        Args:
            session_id: Session identifier
            limit: Max messages to return

        Returns:
            List of messages
        """
        session = cls.get_session(session_id)
        if not session:
            return []

        return session['messages'][-limit:]
