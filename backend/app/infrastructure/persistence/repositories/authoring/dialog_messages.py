"""
Repository for authoring_dialog_messages table (Structured Chat History)
"""
from typing import Dict, List, Optional
import logging

from app.infrastructure.persistence.repositories.core.base import BaseRepository

logger = logging.getLogger(__name__)


class AuthoringDialogMessagesRepository(BaseRepository):
    """Repository for managing structured dialog messages in authoring sessions"""

    @staticmethod
    def create_message(
        session_id: str,
        message_index: int,
        role: str,
        content: str,
        structured_data: Optional[Dict] = None,
        phase: Optional[str] = None,
        ai_provider: Optional[str] = None,
        ai_model: Optional[str] = None,
        tokens_used: Optional[int] = None
    ) -> Optional[str]:
        """
        Create a new dialog message.

        Args:
            session_id: UUID of authoring session
            message_index: Sequential message number
            role: Message role (user, assistant, system)
            content: Message content
            structured_data: Optional structured data
            phase: Optional workflow phase
            ai_provider: Optional AI provider
            ai_model: Optional AI model
            tokens_used: Optional token count

        Returns:
            message_id if successful
        """
        query = """
            INSERT INTO courses.authoring_dialog_messages (
                session_id, message_index, role, content,
                structured_data, phase, ai_provider, ai_model, tokens_used
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING message_id
        """
        try:
            result = AuthoringDialogMessagesRepository.fetch_one(query, (
                session_id, message_index, role, content,
                structured_data or {}, phase, ai_provider, ai_model, tokens_used
            ))
            return result['message_id'] if result else None
        except Exception as e:
            logger.error(f"Error creating dialog message: {e}")
            return None

    @staticmethod
    def get_message_by_id(message_id: str) -> Optional[Dict]:
        """Get dialog message by ID"""
        query = """
            SELECT
                message_id, session_id, message_index,
                role, content, structured_data, phase,
                ai_provider, ai_model, tokens_used,
                references_chapter_id, references_lesson_id,
                created_at
            FROM courses.authoring_dialog_messages
            WHERE message_id = %s
        """
        try:
            return AuthoringDialogMessagesRepository.fetch_one(query, (message_id,))
        except Exception as e:
            logger.error(f"Error fetching dialog message: {e}")
            return None

    @staticmethod
    def get_messages_by_session(
        session_id: str,
        phase: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Get dialog messages for session.

        Args:
            session_id: UUID of authoring session
            phase: Optional filter by phase
            limit: Optional limit

        Returns:
            List of message records
        """
        query = """
            SELECT
                message_id, message_index, role, content,
                structured_data, phase, ai_provider, ai_model,
                tokens_used, created_at
            FROM courses.authoring_dialog_messages
            WHERE session_id = %s
        """
        params = [session_id]

        if phase:
            query += " AND phase = %s"
            params.append(phase)

        query += " ORDER BY message_index ASC"

        if limit:
            query += " LIMIT %s"
            params.append(limit)

        try:
            return AuthoringDialogMessagesRepository.fetch_all(query, tuple(params))
        except Exception as e:
            logger.error(f"Error fetching session messages: {e}")
            return []

    @staticmethod
    def get_next_message_index(session_id: str) -> int:
        """Get next message index for session"""
        query = """
            SELECT COALESCE(MAX(message_index), 0) + 1 as next_index
            FROM courses.authoring_dialog_messages
            WHERE session_id = %s
        """
        try:
            result = AuthoringDialogMessagesRepository.fetch_one(query, (session_id,))
            return result['next_index'] if result else 1
        except Exception as e:
            logger.error(f"Error getting next message index: {e}")
            return 1

    @staticmethod
    def get_message_statistics(session_id: str) -> Dict:
        """Get message statistics for session"""
        query = """
            SELECT
                COUNT(*) as total_messages,
                COUNT(CASE WHEN role = 'user' THEN 1 END) as user_messages,
                COUNT(CASE WHEN role = 'assistant' THEN 1 END) as assistant_messages,
                COUNT(CASE WHEN role = 'system' THEN 1 END) as system_messages,
                COALESCE(SUM(tokens_used), 0) as total_tokens
            FROM courses.authoring_dialog_messages
            WHERE session_id = %s
        """
        try:
            result = AuthoringDialogMessagesRepository.fetch_one(query, (session_id,))
            return result if result else {
                'total_messages': 0,
                'user_messages': 0,
                'assistant_messages': 0,
                'system_messages': 0,
                'total_tokens': 0
            }
        except Exception as e:
            logger.error(f"Error fetching message statistics: {e}")
            return {
                'total_messages': 0,
                'user_messages': 0,
                'assistant_messages': 0,
                'system_messages': 0,
                'total_tokens': 0
            }

    @staticmethod
    def get_recent_context(
        session_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent messages for context.

        Args:
            session_id: UUID of authoring session
            limit: Number of recent messages

        Returns:
            List of recent messages
        """
        query = """
            SELECT
                message_index, role, content,
                structured_data, phase, created_at
            FROM courses.authoring_dialog_messages
            WHERE session_id = %s
            ORDER BY message_index DESC
            LIMIT %s
        """
        try:
            messages = AuthoringDialogMessagesRepository.fetch_all(query, (session_id, limit))
            # Reverse to get chronological order
            return list(reversed(messages))
        except Exception as e:
            logger.error(f"Error fetching recent context: {e}")
            return []
