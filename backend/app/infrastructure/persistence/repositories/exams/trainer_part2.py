"""
ExamTrainer Repository Part 2 — Rotation queries, review, and history.

Continuation of ExamTrainerRepository (trainer.py).
Contains rotation-based question selection, attempt review, and history.

Split from trainer.py to comply with Quality Gate G01 (max 500 lines per file).
"""

from typing import Optional, List, Dict

from app.infrastructure.persistence.database.connection import (
    fetch_one,
    fetch_all,
    execute_query,
)


def _build_topic_filter(topic: Optional[str]):
    """Build SQL fragment + params for optional topic filtering."""
    if topic:
        return "AND %s = ANY(eq.topics)", (topic,)
    return "", ()


class ExamTrainerRotationMixin:
    """Mixin providing rotation queries and review/history for ExamTrainerRepository."""

    # ------------------------------------------------------------------
    # Rotation queries for intelligent practice sessions
    # ------------------------------------------------------------------

    @classmethod
    def find_unseen_questions(
        cls, user_id: str, exam_type: str, topic: Optional[str] = None,
    ) -> List[Dict]:
        """Find questions the user has never seen.

        Uses LEFT JOIN anti-pattern against user_question_stats.
        """
        topic_filter, params = _build_topic_filter(topic)
        query = f"""
            SELECT eq.question_id, eq.question_number, eq.question_text,
                   eq.question_type, eq.scenario_title, eq.scenario_text,
                   eq.topics, eq.points, eq.data
            FROM assessments.exam_questions eq
            JOIN assessments.exams e ON e.exam_id = eq.exam_id
            LEFT JOIN assessments.user_question_stats uqs
                ON uqs.question_id = eq.question_id AND uqs.user_id = %s
            WHERE e.analysis_status = 'ready'
              AND uqs.question_id IS NULL
              {topic_filter}
            ORDER BY RANDOM()
            LIMIT 30
        """
        return fetch_all(query, (user_id, *params))

    @classmethod
    def find_weak_questions(
        cls, user_id: str, exam_type: str, topic: Optional[str] = None,
    ) -> List[Dict]:
        """Find questions the user got wrong (correct rate < 50%)."""
        topic_filter, params = _build_topic_filter(topic)
        query = f"""
            SELECT eq.question_id, eq.question_number, eq.question_text,
                   eq.question_type, eq.scenario_title, eq.scenario_text,
                   eq.topics, eq.points, eq.data,
                   uqs.times_seen, uqs.times_correct
            FROM assessments.exam_questions eq
            JOIN assessments.exams e ON e.exam_id = eq.exam_id
            JOIN assessments.user_question_stats uqs
                ON uqs.question_id = eq.question_id AND uqs.user_id = %s
            WHERE e.analysis_status = 'ready'
              AND uqs.times_seen > 0
              AND uqs.times_correct::float / uqs.times_seen < 0.5
              {topic_filter}
            ORDER BY uqs.times_correct::float / uqs.times_seen ASC, RANDOM()
            LIMIT 20
        """
        return fetch_all(query, (user_id, *params))

    @classmethod
    def find_review_questions(
        cls, user_id: str, exam_type: str, topic: Optional[str] = None,
        days_threshold: int = 7,
    ) -> List[Dict]:
        """Find questions not seen in N days (spaced repetition)."""
        topic_filter, params = _build_topic_filter(topic)
        query = f"""
            SELECT eq.question_id, eq.question_number, eq.question_text,
                   eq.question_type, eq.scenario_title, eq.scenario_text,
                   eq.topics, eq.points, eq.data,
                   uqs.last_seen_at, uqs.times_correct
            FROM assessments.exam_questions eq
            JOIN assessments.exams e ON e.exam_id = eq.exam_id
            JOIN assessments.user_question_stats uqs
                ON uqs.question_id = eq.question_id AND uqs.user_id = %s
            WHERE e.analysis_status = 'ready'
              AND uqs.last_seen_at < NOW() - INTERVAL '%s days'
              {topic_filter}
            ORDER BY uqs.last_seen_at ASC
            LIMIT 20
        """
        return fetch_all(query, (user_id, days_threshold, *params))

    @classmethod
    def upsert_question_stats(
        cls, user_id: str, question_id: str, is_correct: bool,
    ) -> None:
        """Track per-question stats after answer submission."""
        correct_val = 1 if is_correct else 0
        query = """
            INSERT INTO assessments.user_question_stats
                (user_id, question_id, times_seen, times_correct,
                 last_seen_at, last_correct_at)
            VALUES (%s, %s, 1, %s, NOW(), CASE WHEN %s THEN NOW() ELSE NULL END)
            ON CONFLICT (user_id, question_id) DO UPDATE SET
                times_seen = assessments.user_question_stats.times_seen + 1,
                times_correct = assessments.user_question_stats.times_correct
                    + EXCLUDED.times_correct,
                last_seen_at = NOW(),
                last_correct_at = CASE
                    WHEN %s THEN NOW()
                    ELSE assessments.user_question_stats.last_correct_at
                END,
                updated_at = NOW()
        """
        execute_query(
            query, (user_id, question_id, correct_val, is_correct, is_correct),
        )

    @classmethod
    def get_attempt_review(cls, attempt_id: str) -> List[Dict]:
        """Get full review data for a completed attempt (includes solutions)."""
        query = """
            SELECT ea.question_id, ea.user_answer, ea.is_correct,
                   ea.points_earned, ea.flagged_for_review as needs_review,
                   eq.question_text, eq.question_type, eq.data,
                   eq.solution, eq.points as max_points,
                   eq.scenario_title, eq.scenario_text, eq.topics,
                   eq.question_number
            FROM assessments.exam_answers ea
            JOIN assessments.exam_questions eq
                ON ea.question_id = eq.question_id
            WHERE ea.attempt_id = %s
            ORDER BY eq.question_number, ea.answered_at
        """
        return fetch_all(query, (attempt_id,))

    @classmethod
    def get_user_attempt_history(
        cls, user_id: str, limit: int = 20,
    ) -> List[Dict]:
        """Get past attempt summaries for progress tracking."""
        query = """
            SELECT a.attempt_id, a.exam_id, a.started_at,
                   a.completed_at, a.status,
                   r.score, r.total_points, r.percentage, r.passed,
                   e.title as exam_title
            FROM assessments.exam_attempts a
            LEFT JOIN assessments.exam_results r
                ON r.attempt_id = a.attempt_id
            LEFT JOIN assessments.exams e
                ON e.exam_id = a.exam_id
            WHERE a.user_id = %s
              AND a.status = 'completed'
            ORDER BY a.completed_at DESC
            LIMIT %s
        """
        return fetch_all(query, (user_id, limit))
