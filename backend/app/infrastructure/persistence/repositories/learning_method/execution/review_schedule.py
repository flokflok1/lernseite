"""
LernsystemX - Review Schedule Repository

Data access layer for spaced repetition scheduling.
Manages review intervals, mastery scores, and due-review queries.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from psycopg.rows import dict_row

from app.core.bootstrap import extensions

logger = logging.getLogger(__name__)


class ReviewScheduleRepository:
    """
    Repository for learning_methods.review_schedule table.

    Provides CRUD and query methods for spaced repetition scheduling,
    including due-review lookups and mastery aggregations.
    """

    TABLE_NAME = "learning_methods.review_schedule"

    @classmethod
    def find_by_user_method(
        cls,
        user_id: str,
        method_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Find review schedule for a specific user + method pair.

        Args:
            user_id: User UUID
            method_id: Learning method instance UUID

        Returns:
            Schedule record dict or None
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    f"""
                    SELECT *
                    FROM {cls.TABLE_NAME}
                    WHERE user_id = %s AND method_id = %s
                    """,
                    (user_id, method_id),
                )
                return cur.fetchone()

    @staticmethod
    def _build_upsert_params(
        user_id: str, method_id: str, data: dict,
    ) -> tuple:
        """Build parameter tuple for upsert query."""
        return (
            user_id,
            method_id,
            data["easiness_factor"],
            data["interval_days"],
            data["repetition_number"],
            data["next_review_at"],
            data["mastery_score"],
            data.get("current_streak", 0),
            data.get("total_reviews", 0),
            data.get("last_quality"),
            data.get("last_reviewed_at"),
            data["difficulty_level"],
            data.get("confidence", 0.5),
        )

    UPSERT_SQL = f"""
        INSERT INTO {TABLE_NAME}
            (user_id, method_id, easiness_factor, interval_days,
             repetition_number, next_review_at, mastery_score,
             current_streak, total_reviews, last_quality,
             last_reviewed_at, difficulty_level, confidence)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id, method_id) DO UPDATE SET
            easiness_factor = EXCLUDED.easiness_factor,
            interval_days = EXCLUDED.interval_days,
            repetition_number = EXCLUDED.repetition_number,
            next_review_at = EXCLUDED.next_review_at,
            mastery_score = EXCLUDED.mastery_score,
            current_streak = EXCLUDED.current_streak,
            total_reviews = EXCLUDED.total_reviews,
            last_quality = EXCLUDED.last_quality,
            last_reviewed_at = EXCLUDED.last_reviewed_at,
            difficulty_level = EXCLUDED.difficulty_level,
            confidence = EXCLUDED.confidence,
            updated_at = NOW()
        RETURNING *
    """

    @classmethod
    def upsert(
        cls,
        user_id: str,
        method_id: str,
        data: dict,
    ) -> Optional[Dict[str, Any]]:
        """
        Insert or update review schedule for a user+method pair.

        Uses ON CONFLICT (user_id, method_id) DO UPDATE for upsert.

        Args:
            user_id: User UUID
            method_id: Learning method instance UUID
            data: Dict with scheduling fields (easiness_factor,
                  interval_days, repetition_number, next_review_at,
                  mastery_score, difficulty_level, etc.)

        Returns:
            The upserted record dict, or None on failure
        """
        params = cls._build_upsert_params(user_id, method_id, data)
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(cls.UPSERT_SQL, params)
                conn.commit()
                return cur.fetchone()

    @classmethod
    def find_due_reviews(
        cls,
        user_id: str,
        course_id: str = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Find LM instances due for review, ordered by urgency.

        Priority: overdue items first, then by lowest mastery.

        Args:
            user_id: User UUID
            course_id: Optional course filter
            limit: Max results (default 20)

        Returns:
            List of due review records with LM and chapter info
        """
        params: list = [user_id, datetime.utcnow()]
        course_filter = ""
        if course_id:
            course_filter = "AND ch.course_id = %s"
            params.append(course_id)
        params.append(limit)

        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    f"""
                    SELECT rs.*, lmi.method_type, lmi.title AS lm_title,
                           lmi.chapter_id, ch.title AS chapter_title,
                           ch.course_id
                    FROM {cls.TABLE_NAME} rs
                    JOIN learning_methods.learning_method_instances lmi
                        ON lmi.method_id = rs.method_id
                    JOIN courses.chapters ch
                        ON ch.chapter_id = lmi.chapter_id
                    WHERE rs.user_id = %s
                      AND rs.next_review_at <= %s
                      {course_filter}
                    ORDER BY rs.next_review_at ASC,
                             rs.mastery_score ASC
                    LIMIT %s
                    """,
                    params,
                )
                return cur.fetchall()

    @classmethod
    def find_user_mastery_map(
        cls,
        user_id: str,
        course_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Get mastery overview per chapter for a course.

        Args:
            user_id: User UUID
            course_id: Course UUID

        Returns:
            List of chapter mastery aggregates
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    f"""
                    SELECT ch.chapter_id, ch.title AS chapter_title,
                           ch.order_index,
                           AVG(rs.mastery_score) AS avg_mastery,
                           MIN(rs.mastery_score) AS min_mastery,
                           COUNT(*) AS total_lms,
                           COUNT(*) FILTER (WHERE rs.mastery_score >= 80)
                               AS mastered_lms,
                           COUNT(*) FILTER (WHERE rs.next_review_at <= NOW())
                               AS due_reviews,
                           MIN(rs.next_review_at) AS next_review
                    FROM {cls.TABLE_NAME} rs
                    JOIN learning_methods.learning_method_instances lmi
                        ON lmi.method_id = rs.method_id
                    JOIN courses.chapters ch
                        ON ch.chapter_id = lmi.chapter_id
                    WHERE rs.user_id = %s
                      AND ch.course_id = %s
                    GROUP BY ch.chapter_id, ch.title, ch.order_index
                    ORDER BY ch.order_index
                    """,
                    (user_id, course_id),
                )
                return cur.fetchall()

    @classmethod
    def get_review_stats(
        cls,
        user_id: str,
        course_id: str,
    ) -> Dict[str, Any]:
        """
        Summary stats: total, due, mastered, avg mastery.

        Args:
            user_id: User UUID
            course_id: Course UUID

        Returns:
            Dict with total_items, due_count, mastered_count,
            avg_mastery, next_review
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    f"""
                    SELECT COUNT(*) AS total_items,
                           COUNT(*) FILTER (WHERE rs.next_review_at <= NOW())
                               AS due_count,
                           COUNT(*) FILTER (WHERE rs.mastery_score >= 80)
                               AS mastered_count,
                           ROUND(AVG(rs.mastery_score)::numeric, 1)
                               AS avg_mastery,
                           MIN(rs.next_review_at) AS next_review
                    FROM {cls.TABLE_NAME} rs
                    JOIN learning_methods.learning_method_instances lmi
                        ON lmi.method_id = rs.method_id
                    JOIN courses.chapters ch
                        ON ch.chapter_id = lmi.chapter_id
                    WHERE rs.user_id = %s
                      AND ch.course_id = %s
                    """,
                    (user_id, course_id),
                )
                return cur.fetchone() or {}

    @classmethod
    def initialize_for_course(
        cls,
        user_id: str,
        course_id: str,
    ) -> int:
        """
        Create initial review_schedule rows for all LMs in a course.

        Skips already-existing rows via ON CONFLICT DO NOTHING.

        Args:
            user_id: User UUID
            course_id: Course UUID

        Returns:
            Count of newly created schedule rows
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    WITH new_rows AS (
                        INSERT INTO learning_methods.review_schedule
                            (user_id, method_id)
                        SELECT %s, lmi.method_id
                        FROM learning_methods.learning_method_instances lmi
                        JOIN courses.chapters ch
                            ON ch.chapter_id = lmi.chapter_id
                        WHERE ch.course_id = %s
                          AND lmi.published = TRUE
                        ON CONFLICT (user_id, method_id) DO NOTHING
                        RETURNING schedule_id
                    )
                    SELECT COUNT(*) AS created FROM new_rows
                    """,
                    (user_id, course_id),
                )
                conn.commit()
                result = cur.fetchone()
                return result["created"] if result else 0
