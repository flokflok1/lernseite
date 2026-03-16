"""Rotation Service — intelligent question selection for exam trainer.

Selects questions for practice sessions using a priority-based rotation:
1. Never-seen questions (highest priority)
2. Questions answered wrong last time
3. Questions not seen in >7 days (spaced repetition)
4. Random from remaining pool

Target mix: ~40% unseen, ~30% weak, ~30% review
"""
import logging
from typing import Dict, List, Optional

from app.infrastructure.persistence.repositories.exams.trainer import (
    ExamTrainerRepository,
)

logger = logging.getLogger(__name__)

# Default session size
DEFAULT_SESSION_SIZE = 15


class RotationService:
    """Selects questions for practice sessions using intelligent rotation."""

    @staticmethod
    def generate_adaptive_exam(
        user_id: str,
        question_count: int = 20,
        duration_minutes: int = 90,
    ) -> Optional[Dict]:
        """Generate an adaptive exam using the rotation algorithm.

        Creates a proper exam_attempt for tracking.

        Args:
            user_id: Current user ID
            question_count: Number of questions to include
            duration_minutes: Time limit for the exam

        Returns:
            Dict with attempt_id, questions, duration_minutes,
            total_points, question_count — or None if no questions available.
        """
        questions = RotationService.build_practice_session(
            user_id=user_id,
            exam_type='real',
            topic=None,
            count=question_count,
        )

        if not questions:
            return None

        total_points = sum(q.get('points') or 5 for q in questions)

        attempt = ExamTrainerRepository.create_adaptive_attempt(
            user_id=user_id,
            duration_minutes=duration_minutes,
            total_points=total_points,
        )

        if not attempt:
            logger.error(
                "Failed to create adaptive attempt for user=%s", user_id,
            )
            return None

        # Strip solutions so user cannot see answers
        for q in questions:
            q.pop('solution', None)
            q.pop('solution_text', None)

        return {
            'attempt_id': attempt['attempt_id'],
            'questions': questions,
            'duration_minutes': duration_minutes,
            'total_points': total_points,
            'question_count': len(questions),
        }

    @staticmethod
    def build_practice_session(
        user_id: str,
        exam_type: str,
        topic: Optional[str] = None,
        count: int = DEFAULT_SESSION_SIZE,
    ) -> List[Dict]:
        """Build a rotated practice session.

        Args:
            user_id: Current user
            exam_type: Exam type filter (e.g. 'FI_AP1')
            topic: Optional topic filter (None = all topics)
            count: Number of questions to return

        Returns:
            List of question dicts, ordered for practice
        """
        buckets = _fetch_rotation_buckets(user_id, exam_type, topic)

        selected = _select_from_buckets(buckets, count)

        logger.info(
            "Practice session: user=%s, topic=%s, "
            "requested=%d, selected=%d (unseen=%d, weak=%d, review=%d)",
            user_id, topic or 'all', count, len(selected),
            buckets['unseen_used'], buckets['weak_used'],
            buckets['review_used'],
        )

        return selected


def _fetch_rotation_buckets(
    user_id: str, exam_type: str, topic: Optional[str],
) -> Dict:
    """Fetch questions split into rotation buckets."""
    unseen = ExamTrainerRepository.find_unseen_questions(
        user_id, exam_type, topic,
    )
    weak = ExamTrainerRepository.find_weak_questions(
        user_id, exam_type, topic,
    )
    review = ExamTrainerRepository.find_review_questions(
        user_id, exam_type, topic, days_threshold=7,
    )

    return {
        'unseen': unseen,
        'weak': weak,
        'review': review,
        'unseen_used': 0,
        'weak_used': 0,
        'review_used': 0,
    }


def _select_from_buckets(buckets: Dict, count: int) -> List[Dict]:
    """Select questions from buckets with target mix.

    Target: ~40% unseen, ~30% weak, ~30% review.
    If a bucket is exhausted, remaining slots go to other buckets.
    """
    unseen = buckets['unseen']
    weak = buckets['weak']
    review = buckets['review']

    # Calculate target counts
    target_unseen = max(1, round(count * 0.4))
    target_weak = max(1, round(count * 0.3))
    target_review = count - target_unseen - target_weak

    # Take from each bucket (with overflow redistribution)
    picked_unseen = unseen[:target_unseen]
    picked_weak = weak[:target_weak]
    picked_review = review[:target_review]

    selected = picked_unseen + picked_weak + picked_review
    seen_ids = {q['question_id'] for q in selected}

    # Fill remaining slots from any bucket
    remaining = count - len(selected)
    if remaining > 0:
        for pool in [unseen, weak, review]:
            for q in pool:
                if q['question_id'] not in seen_ids:
                    selected.append(q)
                    seen_ids.add(q['question_id'])
                    remaining -= 1
                    if remaining <= 0:
                        break
            if remaining <= 0:
                break

    buckets['unseen_used'] = len(picked_unseen)
    buckets['weak_used'] = len(picked_weak)
    buckets['review_used'] = len(picked_review)

    return selected
