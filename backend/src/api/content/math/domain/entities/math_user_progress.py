"""
Math User Progress Entity (DDD Domain Entity)

Represents user progress for a specific math pattern.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from decimal import Decimal


@dataclass
class MathUserProgress:
    """
    Math User Progress domain entity.

    Tracks user mastery and progress for a specific math pattern
    with spaced repetition scheduling.

    Attributes:
        progress_id: UUID
        user_id: User UUID
        pattern_id: Math pattern UUID
        current_level: Current scaffolding level (1-3)
        total_attempts: Total number of attempts
        correct_attempts: Number of correct attempts
        mastery_score: Mastery percentage (0-100)
        current_streak: Current correct answers streak
        best_streak: Best streak ever achieved
        last_practiced_at: Last practice timestamp
        next_review_at: Next scheduled review timestamp
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    progress_id: str
    user_id: str
    pattern_id: str
    current_level: int = 1
    total_attempts: int = 0
    correct_attempts: int = 0
    mastery_score: Decimal = Decimal('0')
    current_streak: int = 0
    best_streak: int = 0
    last_practiced_at: Optional[datetime] = None
    next_review_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate math user progress entity."""
        if not self.progress_id or not self.progress_id.strip():
            raise ValueError("Progress ID cannot be empty")
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID cannot be empty")
        if not self.pattern_id or not self.pattern_id.strip():
            raise ValueError("Pattern ID cannot be empty")
        if self.current_level < 1 or self.current_level > 3:
            raise ValueError("Current level must be between 1 and 3")
        if self.mastery_score < 0 or self.mastery_score > 100:
            raise ValueError("Mastery score must be between 0 and 100")

    def record_attempt(self, is_correct: bool) -> None:
        """
        Record a practice attempt.

        Args:
            is_correct: Whether the attempt was correct
        """
        self.total_attempts += 1
        self.last_practiced_at = datetime.utcnow()

        if is_correct:
            self.correct_attempts += 1
            self.current_streak += 1
            if self.current_streak > self.best_streak:
                self.best_streak = self.current_streak
        else:
            self.current_streak = 0

        # Recalculate mastery score
        self._update_mastery_score()

        # Schedule next review (spaced repetition)
        self._schedule_next_review()

        self.updated_at = datetime.utcnow()

    def _update_mastery_score(self) -> None:
        """
        Update mastery score based on performance.

        Simple formula: (correct / total) * 100
        """
        if self.total_attempts == 0:
            self.mastery_score = Decimal('0')
        else:
            self.mastery_score = Decimal(
                (self.correct_attempts / self.total_attempts) * 100
            ).quantize(Decimal('0.01'))

    def _schedule_next_review(self) -> None:
        """
        Schedule next review using spaced repetition.

        Intervals based on mastery level:
        - Low mastery (0-60%): 1 day
        - Medium mastery (60-80%): 3 days
        - High mastery (80-100%): 7 days
        """
        now = datetime.utcnow()

        if self.mastery_score < 60:
            interval_days = 1
        elif self.mastery_score < 80:
            interval_days = 3
        else:
            interval_days = 7

        self.next_review_at = now + timedelta(days=interval_days)

    def increase_level(self) -> None:
        """Increase scaffolding level (reduce help)."""
        if self.current_level < 3:
            self.current_level += 1
            self.updated_at = datetime.utcnow()

    def decrease_level(self) -> None:
        """Decrease scaffolding level (increase help)."""
        if self.current_level > 1:
            self.current_level -= 1
            self.updated_at = datetime.utcnow()

    def is_due_for_review(self) -> bool:
        """
        Check if pattern is due for review.

        Returns:
            True if review is due
        """
        if not self.next_review_at:
            return True
        return datetime.utcnow() >= self.next_review_at

    def get_accuracy(self) -> float:
        """
        Calculate accuracy percentage.

        Returns:
            Accuracy as percentage (0-100)
        """
        if self.total_attempts == 0:
            return 0.0
        return (self.correct_attempts / self.total_attempts) * 100
