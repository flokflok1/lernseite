"""
Authoring Service - Main orchestrator

Coordinates all authoring operations:
- Chat processing
- Content preview
- Content saving
- Session management

This module orchestrates the various sub-components of the authoring system.
"""

import logging
from typing import Dict, Any, Optional, List

from app.ki.prompts.authoring import QUICK_PROMPTS

from .exceptions import AuthoringServiceError
from .session_manager import SessionManager
from .chat_processor import ChatProcessor
from .preview_generator import PreviewGenerator
from .content_saver import ContentSaver

logger = logging.getLogger(__name__)


class AuthoringService:
    """
    Universal Authoring Service for chat-based content creation.

    Supports creation of:
    - Chapters with theory
    - Lessons with explanations
    - Tasks/exercises
    - Learning method instances (LM00-LM11)

    Usage:
        >>> service = AuthoringService()
        >>> result = service.process_chat_message(
        ...     course_id="uuid",
        ...     context_type="chapter",
        ...     context_id=None,
        ...     message="Erstelle ein Kapitel über Netzwerktechnik",
        ...     file_context=["file_id_1"],
        ...     session_id="uuid"
        ... )
    """

    def __init__(self, provider: str = "anthropic", model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize authoring service.

        Args:
            provider: AI provider (anthropic, openai)
            model: Model identifier
        """
        self.provider = provider
        self.model = model
        self._chat_processor = ChatProcessor(provider=provider, model=model)

    def process_chat_message(
        self,
        course_id: str,
        context_type: str,
        context_id: Optional[str],
        message: str,
        file_context: List[str],
        session_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message and generate AI response.

        Args:
            course_id: Course UUID
            context_type: Type of content (chapter, lesson, task, learning_method)
            context_id: Existing content ID (None for new creation)
            message: User message
            file_context: List of file IDs for context
            session_id: Chat session ID
            user_id: Optional user ID

        Returns:
            Dict with AI response and optional generated content

        Raises:
            AuthoringServiceError: If processing fails
        """
        return self._chat_processor.process_message(
            course_id=course_id,
            context_type=context_type,
            context_id=context_id,
            message=message,
            file_context=file_context,
            session_id=session_id,
            user_id=user_id
        )

    def generate_preview(
        self,
        content_type: str,
        generated_content: Dict[str, Any],
        format_type: str = 'html'
    ) -> Dict[str, Any]:
        """
        Generate preview of content without saving.

        Args:
            content_type: Type of content (chapter_theory, lesson_explanation, etc.)
            generated_content: Generated content data
            format_type: Output format (html, markdown, json)

        Returns:
            Dict with preview HTML/Markdown/JSON
        """
        return PreviewGenerator.generate(
            content_type=content_type,
            generated_content=generated_content,
            format_type=format_type
        )

    def save_content(
        self,
        content_type: str,
        content_id: Optional[str],
        content_data: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Save generated content to database.

        Args:
            content_type: Type of content
            content_id: Existing content ID (None for new)
            content_data: Content to save
            user_id: User ID

        Returns:
            Dict with saved content info

        Raises:
            ValueError: If content type is unknown
        """
        return ContentSaver.save(
            content_type=content_type,
            content_id=content_id or "",
            content_data=content_data,
            user_id=user_id
        )

    def get_quick_prompts(self, context_type: str) -> List[Dict[str, str]]:
        """
        Get quick prompts for a context type.

        Args:
            context_type: Type of context

        Returns:
            List of quick prompt suggestions
        """
        return QUICK_PROMPTS.get(context_type, QUICK_PROMPTS.get('general', []))

    # Session Management Convenience Methods

    @classmethod
    def get_or_create_session(cls, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get existing session or create new one.

        Args:
            session_id: Optional existing session ID

        Returns:
            Session dict
        """
        return SessionManager.get_or_create_session(session_id)

    @classmethod
    def get_session(cls, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session dict or None if not found
        """
        return SessionManager.get_session(session_id)

    @classmethod
    def update_session(cls, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update session data.

        Args:
            session_id: Session identifier
            updates: Dict of updates

        Returns:
            Updated session

        Raises:
            AuthoringServiceError: If session not found
        """
        return SessionManager.update_session(session_id, updates)


def get_authoring_service(
    provider: str = "anthropic",
    model: str = "claude-3-5-sonnet-20241022"
) -> AuthoringService:
    """
    Get authoring service instance.

    Args:
        provider: AI provider
        model: Model identifier

    Returns:
        AuthoringService instance
    """
    return AuthoringService(provider=provider, model=model)
