"""
Learning Method Repository - Feedback System

User feedback collection and analytics:
- create_feedback: Record user feedback on AI executions
- get_method_feedback: Retrieve feedback for a method
- get_feedback_stats: Aggregate feedback statistics (ratings, helpfulness)

Feedback data used for quality analysis and continuous improvement.
"""

from typing import Dict, Any, Optional, List
from psycopg.rows import dict_row

from app.core.bootstrap import extensions


class LearningMethodFeedbackRepository:
    """
    Feedback collection and analysis for learning methods.
    """

    @classmethod
    def create_feedback(
        cls,
        user_id: str,
        execution_id: str,
        rating: int,
        feedback_text: Optional[str] = None,
        is_helpful: bool = True,
        ai_generated: bool = False,
        course_id: Optional[str] = None,
        chapter_id: Optional[str] = None,
        lesson_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create user feedback on AI execution.

        Args:
            user_id: User ID
            execution_id: Execution ID to rate
            rating: Rating (1-5 stars)
            feedback_text: Optional feedback text
            is_helpful: Was response helpful
            ai_generated: Is feedback AI-generated
            course_id: Course ID (optional context)
            chapter_id: Chapter ID (optional context)
            lesson_id: Lesson ID (optional context)

        Returns:
            Created feedback record

        Raises:
            ValueError: If execution not found
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Get method_id from execution
                cur.execute("""
                    SELECT method_id FROM learning_method_executions
                    WHERE execution_id = %s
                """, (execution_id,))

                execution = cur.fetchone()
                if not execution:
                    raise ValueError(f'Execution {execution_id} not found')

                method_id = execution['method_id']

                # Create feedback
                cur.execute("""
                    INSERT INTO ai_feedback (
                        user_id, execution_id, method_id,
                        course_id, chapter_id, lesson_id,
                        rating, feedback_text, is_helpful, ai_generated
                    ) VALUES (
                        %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s, %s
                    )
                    RETURNING *
                """, (
                    user_id, execution_id, method_id,
                    course_id, chapter_id, lesson_id,
                    rating, feedback_text, is_helpful, ai_generated
                ))

                conn.commit()
                return cur.fetchone()

    @classmethod
    def get_method_feedback(cls, method_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get feedback records for a learning method.

        Args:
            method_id: Learning method ID
            limit: Maximum results (default 50)

        Returns:
            List of feedback records with user info
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT
                        f.*,
                        u.username,
                        u.firstname,
                        u.lastname
                    FROM ai_feedback f
                    JOIN core.users u ON f.user_id = u.user_id
                    WHERE f.method_id = %s
                    ORDER BY f.created_at DESC
                    LIMIT %s
                """, (method_id, limit))

                return cur.fetchall()

    @classmethod
    def get_feedback_stats(cls, method_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get feedback statistics (aggregate ratings and helpfulness).

        Args:
            method_id: Learning method ID (None for all methods)

        Returns:
            {
                'method_id': str | None,
                'total_feedback': int,
                'average_rating': float,
                'helpful_count': int,
                'not_helpful_count': int,
                'rating_distribution': {1: count, 2: count, ...}
            }
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Build query parts
                where_clause = "WHERE method_id = %s" if method_id else ""
                params = (method_id,) if method_id else ()

                # Get total stats
                cur.execute(f"""
                    SELECT
                        COUNT(*) as total_feedback,
                        COALESCE(AVG(rating), 0) as average_rating,
                        SUM(CASE WHEN is_helpful = TRUE THEN 1 ELSE 0 END) as helpful_count,
                        SUM(CASE WHEN is_helpful = FALSE THEN 1 ELSE 0 END) as not_helpful_count
                    FROM ai_feedback
                    {where_clause}
                """, params)

                totals = cur.fetchone()

                # Get rating distribution
                cur.execute(f"""
                    SELECT
                        rating,
                        COUNT(*) as count
                    FROM ai_feedback
                    {where_clause}
                    GROUP BY rating
                    ORDER BY rating
                """, params)

                rating_dist = {row['rating']: row['count'] for row in cur.fetchall()}

                # Fill in missing ratings with 0
                for rating in range(1, 6):
                    if rating not in rating_dist:
                        rating_dist[rating] = 0

                return {
                    'method_id': method_id,
                    'total_feedback': totals['total_feedback'],
                    'average_rating': float(totals['average_rating']),
                    'helpful_count': totals['helpful_count'],
                    'not_helpful_count': totals['not_helpful_count'],
                    'rating_distribution': rating_dist
                }
