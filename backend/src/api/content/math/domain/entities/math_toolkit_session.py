"""
Math Toolkit Session Entity (DDD Domain Entity)

Represents a practice session in the Math Toolkit.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class MathToolkitSession:
    """
    Math Toolkit Session domain entity.

    Represents a user's practice session with scaffolding levels and progress tracking.

    Attributes:
        session_id: UUID
        user_id: User UUID
        course_id: Parent course UUID (optional)
        lesson_id: Parent lesson UUID (optional)
        learning_method_id: Related learning method UUID (optional)
        session_type: Type (tutorial, practice, exam, pattern_recognition, free)
        pattern_id: Related pattern UUID (optional)
        scaffolding_level: 1=full help, 2=hints, 3=independent
        started_at: Session start timestamp
        ended_at: Session end timestamp (NULL if active)
        tasks_completed: Number of tasks completed
        tasks_correct: Number of correct tasks
        hints_used: Number of hints used
    """

    session_id: str
    user_id: str
    session_type: str = 'practice'
    scaffolding_level: int = 1
    course_id: Optional[str] = None
    lesson_id: Optional[str] = None
    learning_method_id: Optional[str] = None
    pattern_id: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    tasks_completed: int = 0
    tasks_correct: int = 0
    hints_used: int = 0

    def __post_init__(self):
        """Validate math toolkit session entity."""
        if not self.session_id or not self.session_id.strip():
            raise ValueError("Session ID cannot be empty")
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID cannot be empty")
        if self.session_type not in ('tutorial', 'practice', 'exam', 'pattern_recognition', 'free'):
            raise ValueError("Invalid session type")
        if self.scaffolding_level < 1 or self.scaffolding_level > 3:
            raise ValueError("Scaffolding level must be between 1 and 3")

    def end_session(self) -> None:
        """End this session."""
        if self.ended_at:
            raise ValueError("Session already ended")
        self.ended_at = datetime.utcnow()

    def complete_task(self, is_correct: bool) -> None:
        """
        Mark a task as completed.

        Args:
            is_correct: Whether the task was completed correctly
        """
        self.tasks_completed += 1
        if is_correct:
            self.tasks_correct += 1

    def use_hint(self) -> None:
        """Increment hint usage counter."""
        self.hints_used += 1

    def increase_scaffolding_level(self) -> None:
        """Increase scaffolding level (reduce help)."""
        if self.scaffolding_level < 3:
            self.scaffolding_level += 1

    def decrease_scaffolding_level(self) -> None:
        """Decrease scaffolding level (increase help)."""
        if self.scaffolding_level > 1:
            self.scaffolding_level -= 1

    def get_accuracy(self) -> float:
        """
        Calculate accuracy percentage.

        Returns:
            Accuracy as percentage (0-100)
        """
        if self.tasks_completed == 0:
            return 0.0
        return (self.tasks_correct / self.tasks_completed) * 100

    def is_active(self) -> bool:
        """Check if session is still active."""
        return self.ended_at is None
