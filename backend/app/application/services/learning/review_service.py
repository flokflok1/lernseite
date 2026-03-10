"""
Review Service — Application Layer.

Orchestrates spaced repetition reviews:
- Initialize SRS when user enrolls in exam course
- Process review results (score -> SM-2 -> next interval)
- Build adaptive review queue (weakest topics first)
- Provide mastery dashboard data
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone

from app.domain.services.spaced_repetition import (
    compute_next_review, quality_from_score,
    initial_state, ReviewState,
)
from app.infrastructure.cache.service import CacheService

logger = logging.getLogger(__name__)

REVIEW_QUEUE_TTL = 300    # 5 min
REVIEW_MASTERY_TTL = 600  # 10 min


class ReviewService:
    """Application service for spaced repetition scheduling."""

    @staticmethod
    def initialize_course_reviews(
        user_id: str, course_id: str,
    ) -> Dict[str, Any]:
        """Initialize review schedule for all LMs in a course.

        Called when user enrolls or starts an exam course.
        Creates review_schedule rows with default SM-2 state.
        """
        from app.infrastructure.persistence.repositories.learning_method.execution.review_schedule import (
            ReviewScheduleRepository,
        )
        count = ReviewScheduleRepository.initialize_for_course(
            user_id, course_id,
        )
        _invalidate_review_cache(user_id)
        logger.info(
            "Initialized %d review items for user %s, course %s",
            count, user_id, course_id,
        )
        return {'initialized': count}

    @staticmethod
    def process_review(
        user_id: str,
        method_id: str,
        score: float,
        time_seconds: int = 0,
        expected_seconds: int = 120,
    ) -> Dict[str, Any]:
        """Process a completed review (score -> SM-2 -> persist)."""
        from app.infrastructure.persistence.repositories.learning_method.execution.review_schedule import (
            ReviewScheduleRepository,
        )

        current_row = _load_or_create_initial(
            ReviewScheduleRepository, user_id, method_id,
        )

        # Convert score to SM-2 quality
        time_ratio = (
            time_seconds / expected_seconds
            if expected_seconds > 0 else 1.0
        )
        quality = quality_from_score(score, time_ratio)

        # Compute next review via SM-2 domain service
        current = _row_to_review_state(current_row)
        new_state = compute_next_review(current, quality)

        # Persist updated state
        upsert_data = _build_upsert_data(
            new_state, quality, current_row,
        )
        result = ReviewScheduleRepository.upsert(
            user_id, method_id, upsert_data,
        )
        _invalidate_review_cache(user_id)

        logger.info(
            "Review processed: user=%s method=%s quality=%d "
            "mastery=%.1f next=%s interval=%dd",
            user_id, method_id, quality,
            new_state.mastery_score,
            new_state.next_review.date(),
            new_state.interval_days,
        )
        return result

    @staticmethod
    def get_review_queue(
        user_id: str,
        course_id: str,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Get prioritized review queue for a user.

        Returns due items sorted by urgency (overdue first,
        then lowest mastery).
        """
        cache_key = CacheService.make_key(
            'REVIEW', user_id, 'queue', course_id or 'all',
        )
        cached = CacheService.cache_get(cache_key)
        if cached:
            return cached

        from app.infrastructure.persistence.repositories.learning_method.execution.review_schedule import (
            ReviewScheduleRepository,
        )
        items = ReviewScheduleRepository.find_due_reviews(
            user_id, course_id, limit,
        )
        stats = ReviewScheduleRepository.get_review_stats(
            user_id, course_id,
        )
        result = {'items': items, 'stats': stats}
        CacheService.cache_set(cache_key, result, ttl=REVIEW_QUEUE_TTL)
        return result

    @staticmethod
    def get_mastery_map(
        user_id: str, course_id: str,
    ) -> List[Dict[str, Any]]:
        """Get per-chapter mastery overview for dashboard."""
        cache_key = CacheService.make_key(
            'REVIEW', user_id, 'mastery', course_id,
        )
        cached = CacheService.cache_get(cache_key)
        if cached:
            return cached

        from app.infrastructure.persistence.repositories.learning_method.execution.review_schedule import (
            ReviewScheduleRepository,
        )
        result = ReviewScheduleRepository.find_user_mastery_map(
            user_id, course_id,
        )
        CacheService.cache_set(cache_key, result, ttl=REVIEW_MASTERY_TTL)
        return result

    @staticmethod
    def get_daily_recall(
        user_id: str, limit: int = 10,
    ) -> Dict[str, Any]:
        """Get due review items across ALL courses for daily recall.

        Unlike get_review_queue (per-course), this returns the most
        urgent items globally — ideal for a daily recall session.
        """
        cache_key = CacheService.make_key('REVIEW', user_id, 'daily')
        cached = CacheService.cache_get(cache_key)
        if cached:
            return cached

        from app.infrastructure.persistence.repositories.learning_method.execution.review_schedule import (
            ReviewScheduleRepository,
        )
        items = ReviewScheduleRepository.find_due_reviews(
            user_id, course_id=None, limit=limit,
        )
        result = {
            'items': items,
            'count': len(items),
        }
        CacheService.cache_set(cache_key, result, ttl=REVIEW_QUEUE_TTL)
        return result

    @staticmethod
    def get_method_difficulty(
        user_id: str, method_id: str,
    ) -> Dict[str, Any]:
        """Get difficulty info for a specific LM from review_schedule."""
        from app.infrastructure.persistence.repositories.learning_method.execution.review_schedule import (
            ReviewScheduleRepository,
        )
        row = ReviewScheduleRepository.find_by_user_method(user_id, method_id)
        if not row:
            return {
                'difficulty_level': 'medium',
                'mastery_score': 0,
                'confidence': 0,
                'total_reviews': 0,
            }
        return {
            'difficulty_level': row.get('difficulty_level', 'medium'),
            'mastery_score': row.get('mastery_score', 0),
            'confidence': row.get('confidence', 0),
            'total_reviews': row.get('total_reviews', 0),
        }

    @staticmethod
    def get_course_difficulty(
        user_id: str, course_id: str,
    ) -> Dict[str, Any]:
        """Get aggregated difficulty recommendation for a course."""
        from app.infrastructure.persistence.repositories.learning_method.execution.review_schedule import (
            ReviewScheduleRepository,
        )
        stats = ReviewScheduleRepository.get_review_stats(user_id, course_id)
        avg = stats.get('avg_mastery', 0) if stats else 0
        if avg >= 80:
            level = 'hard'
        elif avg >= 50:
            level = 'medium'
        else:
            level = 'easy'
        return {
            'recommended_difficulty': level,
            'avg_mastery': avg,
            'total_items': stats.get('total_items', 0) if stats else 0,
            'mastered_count': stats.get('mastered_count', 0) if stats else 0,
        }

    @staticmethod
    def get_stats(
        user_id: str, course_id: str,
    ) -> Dict[str, Any]:
        """Get summary review statistics for a course."""
        cache_key = CacheService.make_key(
            'REVIEW', user_id, 'stats', course_id,
        )
        cached = CacheService.cache_get(cache_key)
        if cached:
            return cached

        from app.infrastructure.persistence.repositories.learning_method.execution.review_schedule import (
            ReviewScheduleRepository,
        )
        result = ReviewScheduleRepository.get_review_stats(
            user_id, course_id,
        )
        CacheService.cache_set(cache_key, result, ttl=REVIEW_QUEUE_TTL)
        return result


def _invalidate_review_cache(user_id: str) -> None:
    """Invalidate all review cache keys for a user."""
    pattern = CacheService.make_key('REVIEW', user_id, '*')
    CacheService.cache_delete_pattern(pattern)


# ------------------------------------------------------------------
# Private helpers (keep methods under 50 LOC)
# ------------------------------------------------------------------

def _load_or_create_initial(repo_cls, user_id: str, method_id: str) -> dict:
    """Load existing review row or create initial state via upsert."""
    current_row = repo_cls.find_by_user_method(user_id, method_id)
    if current_row:
        return current_row

    state = initial_state()
    return repo_cls.upsert(
        user_id, method_id, {
            'easiness_factor': state.easiness_factor,
            'interval_days': state.interval_days,
            'repetition_number': state.repetition,
            'next_review_at': state.next_review,
            'mastery_score': state.mastery_score,
            'difficulty_level': state.difficulty_level,
        },
    )


def _row_to_review_state(row: dict) -> ReviewState:
    """Convert a DB row dict to a ReviewState value object."""
    return ReviewState(
        easiness_factor=row.get('easiness_factor', 2.5),
        interval_days=row.get('interval_days', 1),
        repetition=row.get('repetition_number', 0),
        next_review=row.get('next_review_at') or datetime.now(timezone.utc),
        mastery_score=row.get('mastery_score', 0.0),
        difficulty_level=row.get('difficulty_level', 'medium'),
    )


def _build_upsert_data(
    new_state: ReviewState, quality: int, current_row: dict,
) -> dict:
    """Build the dict for ReviewScheduleRepository.upsert."""
    streak = current_row.get('current_streak', 0)
    streak = streak + 1 if quality >= 3 else 0

    return {
        'easiness_factor': new_state.easiness_factor,
        'interval_days': new_state.interval_days,
        'repetition_number': new_state.repetition,
        'next_review_at': new_state.next_review,
        'mastery_score': new_state.mastery_score,
        'current_streak': streak,
        'total_reviews': current_row.get('total_reviews', 0) + 1,
        'last_quality': quality,
        'last_reviewed_at': datetime.now(timezone.utc),
        'difficulty_level': new_state.difficulty_level,
        'confidence': min(1.0, new_state.mastery_score / 100),
    }
