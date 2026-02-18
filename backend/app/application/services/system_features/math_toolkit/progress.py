"""
User progress and mastery tracking module.

Tracks user learning progress, mastery scores, streaks, and adaptive leveling.
"""

from typing import Dict, List, Optional
import logging

from app.infrastructure.persistence.repositories.core.base import BaseRepository

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
        query = """
            SELECT
                up.progress_id, up.current_level, up.total_attempts,
                up.correct_attempts, up.mastery_score,
                up.current_streak, up.best_streak,
                up.last_practiced_at, up.next_review_at,
                p.pattern_code, p.name as pattern_name,
                c.category_code, c.name as category_name
            FROM math_user_progress up
            JOIN math_patterns p ON up.pattern_id = p.pattern_id
            LEFT JOIN math_pattern_categories c ON p.category_id = c.category_id
            WHERE up.user_id = %s
              AND ($2::uuid IS NULL OR up.pattern_id = $2)
            ORDER BY up.mastery_score DESC, up.last_practiced_at DESC
        """
        return BaseRepository.fetch_all(query, (user_id, pattern_id)) or []

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
        query_get = """
            SELECT progress_id, current_level, total_attempts, correct_attempts,
                   mastery_score, current_streak, best_streak
            FROM math_user_progress
            WHERE user_id = %s AND pattern_id = %s
        """
        progress = BaseRepository.fetch_one(query_get, (user_id, pattern_id))

        if not progress:
            # Create new progress record
            query_insert = """
                INSERT INTO math_user_progress (user_id, pattern_id)
                VALUES (%s, %s)
                RETURNING progress_id, current_level, total_attempts,
                          correct_attempts, mastery_score, current_streak,
                          best_streak
            """
            progress = BaseRepository.fetch_one(query_insert, (user_id, pattern_id))

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
        query_update = """
            UPDATE math_user_progress
            SET current_level = %s,
                total_attempts = %s,
                correct_attempts = %s,
                mastery_score = %s,
                current_streak = %s,
                best_streak = %s,
                last_practiced_at = NOW(),
                next_review_at = NOW() + INTERVAL '1 day' * %s
            WHERE user_id = %s AND pattern_id = %s
        """
        BaseRepository.execute(query_update, (
            new_level, total, correct, mastery, streak, best_streak,
            review_days, user_id, pattern_id
        ))

        return {
            'current_level': new_level,
            'total_attempts': total,
            'correct_attempts': correct,
            'mastery_score': round(mastery, 1),
            'current_streak': streak,
            'best_streak': best_streak,
            'level_changed': new_level != progress['current_level']
        }
