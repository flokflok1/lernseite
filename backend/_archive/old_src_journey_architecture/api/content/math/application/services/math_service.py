"""
Math Service (Application Layer)

Business logic for math toolkit operations.
ALL data loaded dynamically from database - NO hardcoded values.

Uses Repository Pattern for database access.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from src.api.content.math.domain.entities.math_pattern_category import MathPatternCategory
from src.api.content.math.domain.entities.math_pattern import MathPattern
from src.api.content.math.domain.entities.math_formula import MathFormula
from src.api.content.math.domain.entities.math_toolkit_session import MathToolkitSession
from src.api.content.math.domain.entities.math_user_progress import MathUserProgress
from src.api.content.math.infrastructure.repositories.math_repository import MathRepository
from src.api.content.math.infrastructure.repositories.math_repository_part2 import MathRepositoryPart2
from src.core.events import EventBus, EventType, DomainEvent


class MathService:
    """
    Math service for business logic.

    ALL configurations and values loaded from database dynamically.
    NO hardcoded patterns, formulas, or categories.
    """

    # ============================================================================
    # PATTERN CATEGORIES
    # ============================================================================

    @staticmethod
    def get_category_by_id(category_id: str) -> Optional[MathPatternCategory]:
        """Get math pattern category by ID."""
        return MathRepository.find_category_by_id(category_id)

    @staticmethod
    def get_category_by_code(category_code: str) -> Optional[MathPatternCategory]:
        """Get math pattern category by code."""
        return MathRepository.find_category_by_code(category_code)

    @staticmethod
    def list_categories(active_only: bool = True) -> List[MathPatternCategory]:
        """List all math pattern categories."""
        return MathRepository.find_all_categories(active_only=active_only)

    # ============================================================================
    # PATTERNS
    # ============================================================================

    @staticmethod
    def get_pattern_by_id(pattern_id: str) -> Optional[MathPattern]:
        """Get math pattern by ID."""
        return MathRepository.find_pattern_by_id(pattern_id)

    @staticmethod
    def get_pattern_by_code(pattern_code: str) -> Optional[MathPattern]:
        """Get math pattern by code."""
        return MathRepository.find_pattern_by_code(pattern_code)

    @staticmethod
    def list_patterns(
        category_id: Optional[str] = None,
        difficulty: Optional[int] = None,
        ihk_relevant: Optional[bool] = None,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[MathPattern]:
        """List math patterns with filters."""
        return MathRepository.find_all_patterns(
            category_id=category_id,
            difficulty=difficulty,
            ihk_relevant=ihk_relevant,
            active_only=active_only,
            limit=limit,
            offset=offset
        )

    # ============================================================================
    # FORMULAS
    # ============================================================================

    @staticmethod
    def get_formula_by_id(formula_id: str) -> Optional[MathFormula]:
        """Get math formula by ID."""
        return MathRepositoryPart2.find_formula_by_id(formula_id)

    @staticmethod
    def list_formulas(
        category_id: Optional[str] = None,
        pattern_id: Optional[str] = None,
        favorites_only: bool = False,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[MathFormula]:
        """List math formulas with filters."""
        return MathRepositoryPart2.find_all_formulas(
            category_id=category_id,
            pattern_id=pattern_id,
            favorites_only=favorites_only,
            active_only=active_only,
            limit=limit,
            offset=offset
        )

    # ============================================================================
    # SESSIONS
    # ============================================================================

    @staticmethod
    def get_session_by_id(session_id: str) -> Optional[MathToolkitSession]:
        """Get math toolkit session by ID."""
        return MathRepositoryPart2.find_session_by_id(session_id)

    @staticmethod
    def list_sessions_by_user(
        user_id: str,
        active_only: bool = False,
        limit: int = 50
    ) -> List[MathToolkitSession]:
        """List math toolkit sessions for a user."""
        return MathRepositoryPart2.find_sessions_by_user(
            user_id=user_id,
            active_only=active_only,
            limit=limit
        )

    @staticmethod
    def create_session(
        user_id: str,
        session_type: str = 'practice',
        scaffolding_level: int = 1,
        pattern_id: Optional[str] = None,
        course_id: Optional[str] = None,
        lesson_id: Optional[str] = None,
        learning_method_id: Optional[str] = None
    ) -> MathToolkitSession:
        """
        Create new math toolkit session.

        Args:
            user_id: User UUID
            session_type: Type (tutorial, practice, exam, pattern_recognition, free)
            scaffolding_level: 1=full help, 2=hints, 3=independent
            pattern_id: Related pattern UUID (optional)
            course_id: Parent course UUID (optional)
            lesson_id: Parent lesson UUID (optional)
            learning_method_id: Related learning method UUID (optional)

        Returns:
            Created MathToolkitSession
        """
        import uuid
        session = MathToolkitSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            session_type=session_type,
            scaffolding_level=scaffolding_level,
            pattern_id=pattern_id,
            course_id=course_id,
            lesson_id=lesson_id,
            learning_method_id=learning_method_id,
            started_at=datetime.utcnow()
        )

        created_session = MathRepositoryPart2.create_session(session)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.MATH_SESSION_STARTED,
            aggregate_id=created_session.session_id,
            occurred_at=datetime.utcnow(),
            data={
                'user_id': created_session.user_id,
                'session_type': created_session.session_type,
                'pattern_id': created_session.pattern_id
            }
        )
        EventBus.publish(event)

        return created_session

    @staticmethod
    def end_session(
        session_id: str,
        user_id: str
    ) -> MathToolkitSession:
        """
        End a math toolkit session.

        Args:
            session_id: Session UUID
            user_id: User UUID (for verification)

        Returns:
            Updated MathToolkitSession

        Raises:
            ValueError: If session not found or not owned by user
        """
        session = MathRepositoryPart2.find_session_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if session.user_id != user_id:
            raise ValueError(f"Session {session_id} not owned by user {user_id}")

        session.end_session()
        updated_session = MathRepositoryPart2.update_session(session)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.MATH_SESSION_ENDED,
            aggregate_id=updated_session.session_id,
            occurred_at=datetime.utcnow(),
            data={
                'user_id': updated_session.user_id,
                'tasks_completed': updated_session.tasks_completed,
                'tasks_correct': updated_session.tasks_correct,
                'accuracy': updated_session.get_accuracy()
            }
        )
        EventBus.publish(event)

        return updated_session

    # ============================================================================
    # USER PROGRESS
    # ============================================================================

    @staticmethod
    def get_user_progress(
        user_id: str,
        pattern_id: str
    ) -> Optional[MathUserProgress]:
        """Get user progress for a specific pattern."""
        return MathRepositoryPart2.find_progress_by_user_and_pattern(
            user_id=user_id,
            pattern_id=pattern_id
        )

    @staticmethod
    def get_all_user_progress(user_id: str) -> List[MathUserProgress]:
        """Get all user progress for all patterns."""
        return MathRepositoryPart2.find_all_progress_by_user(user_id)

    @staticmethod
    def create_or_update_progress(
        user_id: str,
        pattern_id: str,
        is_correct: bool
    ) -> MathUserProgress:
        """
        Create or update user progress after a practice attempt.

        Args:
            user_id: User UUID
            pattern_id: Pattern UUID
            is_correct: Whether the attempt was correct

        Returns:
            Updated MathUserProgress
        """
        # Try to find existing progress
        progress = MathRepositoryPart2.find_progress_by_user_and_pattern(
            user_id=user_id,
            pattern_id=pattern_id
        )

        if not progress:
            # Create new progress
            import uuid
            progress = MathUserProgress(
                progress_id=str(uuid.uuid4()),
                user_id=user_id,
                pattern_id=pattern_id,
                current_level=1,
                created_at=datetime.utcnow()
            )
            progress.record_attempt(is_correct)
            return MathRepositoryPart2.create_progress(progress)
        else:
            # Update existing progress
            progress.record_attempt(is_correct)
            return MathRepositoryPart2.update_progress(progress)

    @staticmethod
    def get_due_reviews(user_id: str) -> List[MathUserProgress]:
        """
        Get patterns that are due for review (spaced repetition).

        Args:
            user_id: User UUID

        Returns:
            List of MathUserProgress that are due for review
        """
        all_progress = MathRepositoryPart2.find_all_progress_by_user(user_id)
        return [p for p in all_progress if p.is_due_for_review()]
