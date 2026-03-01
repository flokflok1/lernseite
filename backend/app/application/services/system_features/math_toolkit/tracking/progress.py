"""
User progress and mastery tracking module.

Tracks user learning progress, mastery scores, streaks, and adaptive leveling.
"""

from typing import Dict, List, Optional
import logging

from app.infrastructure.persistence.repositories.math_toolkit import (
    MathPatternsProgressRepository
)

logger = logging.getLogger(__name__)


class ProgressTracker:
    """Tracks user progress and mastery in patterns."""

    # Mastery thresholds for level advancement
    MASTERY_ADVANCE = 80  # Min mastery % to advance
    STREAK_THRESHOLD = 3  # Min streak to advance
    MAX_LEVEL = 3
    MIN_LEVEL = 1
    MASTERY_DEMOTE = 40  # Max mastery % before demotion

    @staticmethod
    def get_user_progress(
        user_id: str,
        pattern_id: str = None
    ) -> List[Dict]:
        """
        Retrieve user progress (optionally filtered by pattern).

        Args:
            user_id: User identifier
            pattern_id: Optional pattern filter

        Returns:
            List of progress dictionaries
        """
        return MathPatternsProgressRepository.get_user_progress(user_id, pattern_id)

    @staticmethod
    def update_user_progress(
        user_id: str,
        pattern_id: str,
        is_correct: bool,
        update_level: bool = True
    ) -> Dict:
        """
        Update user progress after an attempt.

        Implements spaced repetition algorithm where review intervals
        are based on mastery score.

        Args:
            user_id: User identifier
            pattern_id: Pattern identifier
            is_correct: Whether attempt was correct
            update_level: Whether to recalculate level

        Returns:
            Updated progress dictionary with new scores
        """
        # Get or create progress
        progress = MathPatternsProgressRepository.get_progress_record(
            user_id, pattern_id
        )

        if not progress:
            progress = MathPatternsProgressRepository.insert_progress_record(
                user_id, pattern_id
            )

        # Calculate new metrics
        total = progress['total_attempts'] + 1
        correct = progress['correct_attempts'] + (1 if is_correct else 0)
        streak = (progress['current_streak'] + 1) if is_correct else 0
        best_streak = max(progress['best_streak'], streak)

        # Calculate mastery (weighted average)
        mastery = min(100, (correct / total) * 100) if total > 0 else 0

        # Determine level change
        new_level = progress['current_level']
        if update_level:
            if (mastery >= ProgressTracker.MASTERY_ADVANCE and
                    streak >= ProgressTracker.STREAK_THRESHOLD and
                    new_level < ProgressTracker.MAX_LEVEL):
                new_level = min(ProgressTracker.MAX_LEVEL, new_level + 1)
            elif mastery < ProgressTracker.MASTERY_DEMOTE and new_level > ProgressTracker.MIN_LEVEL:
                new_level = max(ProgressTracker.MIN_LEVEL, new_level - 1)

        # Spaced repetition: review interval based on mastery
        review_days = int(1 + (mastery / 20))

        # Update database
        MathPatternsProgressRepository.update_progress(
            user_id, pattern_id, new_level, total, correct,
            mastery, streak, best_streak, review_days
        )

        return {
            'current_level': new_level,
            'total_attempts': total,
            'correct_attempts': correct,
            'mastery_score': round(mastery, 1),
            'current_streak': streak,
            'best_streak': best_streak,
            'level_changed': new_level != progress['current_level']
        }
