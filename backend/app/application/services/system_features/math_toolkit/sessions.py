"""
Session management module.

Handles toolkit sessions: creation, lifecycle, and statistics tracking.
"""

from typing import Dict, Optional, List
import logging

from app.infrastructure.persistence.repositories.math_toolkit import (
    MathSessionsStepsRepository
)

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages Math Toolkit sessions."""

    @staticmethod
    def start_session(
        user_id: str,
        session_type: str = 'practice',
        pattern_id: str = None,
        scaffolding_level: int = 1,
        course_id: str = None,
        lesson_id: str = None
    ) -> Optional[str]:
        """
        Start new toolkit session.

        Args:
            user_id: User identifier
            session_type: Type of session (practice, tutorial, etc.)
            pattern_id: Optional specific pattern
            scaffolding_level: Scaffolding level (1-3)
            course_id: Optional course context
            lesson_id: Optional lesson context

        Returns:
            New session_id or None if failed
        """
        result = MathSessionsStepsRepository.insert_session(
            user_id, session_type, pattern_id, scaffolding_level,
            course_id, lesson_id
        )
        return str(result['session_id']) if result else None

    @staticmethod
    def end_session(session_id: str) -> bool:
        """
        End an active session.

        Args:
            session_id: Session identifier

        Returns:
            Success status
        """
        return MathSessionsStepsRepository.end_session(session_id)

    @staticmethod
    def get_session(session_id: str) -> Optional[Dict]:
        """
        Retrieve session details.

        Args:
            session_id: Session identifier

        Returns:
            Session dictionary or None
        """
        return MathSessionsStepsRepository.get_session(session_id)

    @staticmethod
    def update_session_stats(
        session_id: str,
        tasks_completed: int = None,
        tasks_correct: int = None,
        hints_used: int = None
    ) -> bool:
        """
        Update session statistics.

        Args:
            session_id: Session identifier
            tasks_completed: Total tasks completed
            tasks_correct: Tasks answered correctly
            hints_used: Hints shown to user

        Returns:
            Success status
        """
        updates = []
        params: List = []

        if tasks_completed is not None:
            updates.append("tasks_completed = %s")
            params.append(tasks_completed)
        if tasks_correct is not None:
            updates.append("tasks_correct = %s")
            params.append(tasks_correct)
        if hints_used is not None:
            updates.append("hints_used = %s")
            params.append(hints_used)

        if not updates:
            return False

        return MathSessionsStepsRepository.update_session_stats(
            session_id, updates, params
        )
