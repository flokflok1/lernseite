"""
Exam Entity (DDD Domain Entity)

Represents an exam/assessment in the system.
All exam data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal


@dataclass
class Exam:
    """
    Exam domain entity.

    All exam attributes loaded dynamically from database.
    NO hardcoded configurations.

    Attributes:
        exam_id: UUID
        course_id: Parent course UUID
        chapter_id: Optional chapter UUID
        created_by: Creator user UUID
        exam_type: Type of exam (from DB: simulation, real, custom, practice, quiz)
        title: Exam title
        description: Exam description
        instructions: Instructions for exam takers
        duration_minutes: Time limit in minutes
        passing_score: Minimum score to pass (percentage)
        total_points: Total possible points
        randomize_questions: Randomize question order
        show_results_immediately: Show results after submission
        allow_review: Allow reviewing answers after completion
        max_attempts: Maximum attempts allowed (None = unlimited)
        settings: JSONB settings (proctoring, calculator, notes, etc.)
        published: Publication status
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    exam_id: str
    course_id: str
    exam_type: str  # Loaded from DB, not hardcoded
    title: str
    duration_minutes: int
    passing_score: Decimal
    created_by: str
    chapter_id: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    total_points: Optional[Decimal] = None
    randomize_questions: bool = False
    show_results_immediately: bool = True
    allow_review: bool = True
    max_attempts: Optional[int] = None
    settings: Optional[Dict[str, Any]] = None
    published: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate exam entity."""
        if not self.exam_id or not self.exam_id.strip():
            raise ValueError("Exam ID cannot be empty")
        if not self.course_id or not self.course_id.strip():
            raise ValueError("Course ID is required")
        if not self.created_by or not self.created_by.strip():
            raise ValueError("Creator ID is required")
        if not self.exam_type or not self.exam_type.strip():
            raise ValueError("Exam type is required")
        if not self.title or not self.title.strip():
            raise ValueError("Exam title cannot be empty")
        if self.duration_minutes <= 0:
            raise ValueError("Duration must be positive")
        if self.passing_score < 0 or self.passing_score > 100:
            raise ValueError("Passing score must be between 0 and 100")
        if self.max_attempts is not None and self.max_attempts <= 0:
            raise ValueError("Max attempts must be positive")

    def publish(self) -> None:
        """
        Publish exam.

        Business rule: Can only publish if not already published.
        """
        if self.published:
            raise ValueError(f"Exam {self.exam_id} is already published")

        self.published = True
        self.updated_at = datetime.utcnow()

    def unpublish(self) -> None:
        """Unpublish exam."""
        self.published = False
        self.updated_at = datetime.utcnow()

    def update_metadata(self, **kwargs) -> None:
        """
        Update exam metadata.

        Args:
            **kwargs: Fields to update
        """
        allowed_fields = {
            'title', 'description', 'instructions', 'duration_minutes',
            'passing_score', 'total_points', 'randomize_questions',
            'show_results_immediately', 'allow_review', 'max_attempts'
        }

        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)

        self.updated_at = datetime.utcnow()

    def update_settings(self, settings: Dict[str, Any]) -> None:
        """
        Update exam settings.

        Args:
            settings: New JSONB settings
        """
        self.settings = settings
        self.updated_at = datetime.utcnow()

    def is_unlimited_attempts(self) -> bool:
        """Check if exam has unlimited attempts."""
        return self.max_attempts is None

    def can_be_taken_by(
        self,
        user_id: str,
        is_enrolled: bool,
        user_role: str,
        attempts_count: int = 0
    ) -> bool:
        """
        Check if user can take this exam.

        Args:
            user_id: User ID to check
            is_enrolled: Whether user is enrolled in course
            user_role: User role
            attempts_count: Number of attempts already made

        Returns:
            True if user can take exam
        """
        # Admin can always take
        if user_role == 'admin':
            return True

        # Must be published
        if not self.published:
            return False

        # Must be enrolled
        if not is_enrolled:
            return False

        # Check max attempts
        if self.max_attempts is not None and attempts_count >= self.max_attempts:
            return False

        return True

    def get_exam_summary(self) -> Dict[str, Any]:
        """
        Get summary of exam configuration.

        Returns:
            Summary dict with key information
        """
        return {
            'exam_id': self.exam_id,
            'title': self.title,
            'exam_type': self.exam_type,
            'duration_minutes': self.duration_minutes,
            'passing_score': float(self.passing_score),
            'total_points': float(self.total_points) if self.total_points else None,
            'max_attempts': self.max_attempts,
            'published': self.published,
            'settings': {
                'randomize_questions': self.randomize_questions,
                'show_results_immediately': self.show_results_immediately,
                'allow_review': self.allow_review
            }
        }
