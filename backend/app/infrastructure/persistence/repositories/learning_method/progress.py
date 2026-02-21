"""
LernsystemX - Learning Method Progress Repository

Data access layer for learning method progress tracking.
Stores user progress data for learning method completions.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.core.bootstrap import extensions


class LearningMethodProgressRepository:
    """
    Repository for learning_methods.learning_method_progress table.

    Tracks user progress and completion data for learning method instances.
    """

    TABLE_NAME = "learning_methods.learning_method_progress"

    @classmethod
    def find_by_user_and_method(
        cls,
        user_id: str,
        method_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find progress record for user and method.

        Args:
            user_id: User UUID
            method_id: Learning method instance UUID

        Returns:
            Progress record or None
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(f"""
                    SELECT *
                    FROM {cls.TABLE_NAME}
                    WHERE user_id = %s AND method_id = %s
                """, (user_id, method_id))
                return cur.fetchone()

    @classmethod
    def upsert_progress(
        cls,
        user_id: str,
        method_id: str,
        score: Optional[float],
        duration_seconds: int,
        state_snapshot: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Insert or update learning progress.

        On conflict (user_id, method_id), updates:
        - score: keeps the GREATEST of old and new score
        - duration_seconds: replaces with new value
        - completed_at: updates to NOW()
        - attempts: increments by 1

        Args:
            user_id: User UUID
            method_id: Learning method instance UUID
            score: Optional score (0-100)
            duration_seconds: Time spent in seconds
            state_snapshot: Optional final state snapshot

        Returns:
            True if successful, False otherwise
        """
        try:
            with extensions.db_pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"""
                        INSERT INTO {cls.TABLE_NAME}
                        (user_id, method_id, score, duration_seconds, completed_at, state_snapshot)
                        VALUES (%s, %s, %s, %s, NOW(), %s)
                        ON CONFLICT (user_id, method_id)
                        DO UPDATE SET
                            score = GREATEST({cls.TABLE_NAME}.score, EXCLUDED.score),
                            duration_seconds = EXCLUDED.duration_seconds,
                            completed_at = NOW(),
                            attempts = {cls.TABLE_NAME}.attempts + 1
                    """, (
                        user_id,
                        method_id,
                        score,
                        duration_seconds,
                        Jsonb(state_snapshot) if state_snapshot else None
                    ))
                    conn.commit()
                    return True
        except Exception:
            return False

    @classmethod
    def get_user_progress_for_course(
        cls,
        user_id: str,
        course_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all progress records for a user in a course.

        Args:
            user_id: User UUID
            course_id: Course UUID

        Returns:
            List of progress records with method info
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(f"""
                    SELECT
                        p.*,
                        lmi.method_type,
                        lmi.lesson_id
                    FROM {cls.TABLE_NAME} p
                    JOIN learning_methods.learning_method_instances lmi
                        ON p.method_id = lmi.method_id
                    JOIN courses.lessons l ON lmi.lesson_id = l.lesson_id
                    JOIN courses.chapters ch ON l.chapter_id = ch.chapter_id
                    WHERE p.user_id = %s AND ch.course_id = %s
                    ORDER BY p.completed_at DESC
                """, (user_id, course_id))
                return cur.fetchall()

    @classmethod
    def get_completion_stats(
        cls,
        user_id: str,
        method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get completion statistics for a user.

        Args:
            user_id: User UUID
            method_id: Optional filter by method

        Returns:
            Stats dict with total_attempts, avg_score, best_score, etc.
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                if method_id:
                    cur.execute(f"""
                        SELECT
                            COUNT(*) as total_completions,
                            COALESCE(SUM(attempts), 0) as total_attempts,
                            AVG(score) as avg_score,
                            MAX(score) as best_score,
                            SUM(duration_seconds) as total_duration
                        FROM {cls.TABLE_NAME}
                        WHERE user_id = %s AND method_id = %s
                    """, (user_id, method_id))
                else:
                    cur.execute(f"""
                        SELECT
                            COUNT(*) as total_completions,
                            COALESCE(SUM(attempts), 0) as total_attempts,
                            AVG(score) as avg_score,
                            MAX(score) as best_score,
                            SUM(duration_seconds) as total_duration
                        FROM {cls.TABLE_NAME}
                        WHERE user_id = %s
                    """, (user_id,))

                return cur.fetchone() or {}
