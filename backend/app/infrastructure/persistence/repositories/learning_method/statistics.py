"""
Learning Method Repository - Statistics and Reporting

Query and reporting methods for usage analysis:
- get_user_token_usage: User token consumption statistics
- get_lesson_executions: Execution history for a lesson
- delete_execution: Remove execution record
- get_statistics: Overall method statistics

Used for analytics, billing, and performance monitoring.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from psycopg.rows import dict_row

from app.core.bootstrap.extensions import db_pool


class LearningMethodStatisticsRepository:
    """
    Statistics and analytics for learning methods.
    """

    @classmethod
    def get_user_token_usage(
        cls,
        user_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get user's token usage statistics over a period.

        Args:
            user_id: User ID
            period_days: Period in days (default 30)

        Returns:
            {
                'user_id': str,
                'total_tokens': int,
                'total_cost_eur': float,
                'total_requests': int,
                'by_method': {method_name: token_count},
                'by_provider': {provider: token_count},
                'by_model': {model: token_count},
                'period_start': datetime,
                'period_end': datetime
            }
        """
        period_start = datetime.now() - timedelta(days=period_days)

        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Get total stats
                cur.execute("""
                    SELECT
                        COALESCE(SUM(total_tokens), 0) as total_tokens,
                        COALESCE(SUM(cost_eur), 0) as total_cost_eur,
                        COUNT(*) as total_requests
                    FROM ai_token_usage
                    WHERE user_id = %s AND used_at >= %s
                """, (user_id, period_start))

                totals = cur.fetchone()

                # Get usage by method
                cur.execute("""
                    SELECT
                        method_name,
                        SUM(total_tokens) as tokens
                    FROM ai_token_usage
                    WHERE user_id = %s AND used_at >= %s
                    GROUP BY method_name
                    ORDER BY tokens DESC
                """, (user_id, period_start))

                by_method = {row['method_name']: row['tokens'] for row in cur.fetchall()}

                # Get usage by provider
                cur.execute("""
                    SELECT
                        provider,
                        SUM(total_tokens) as tokens
                    FROM ai_token_usage
                    WHERE user_id = %s AND used_at >= %s
                    GROUP BY provider
                    ORDER BY tokens DESC
                """, (user_id, period_start))

                by_provider = {row['provider']: row['tokens'] for row in cur.fetchall()}

                # Get usage by model
                cur.execute("""
                    SELECT
                        model,
                        SUM(total_tokens) as tokens
                    FROM ai_token_usage
                    WHERE user_id = %s AND used_at >= %s
                    GROUP BY model
                    ORDER BY tokens DESC
                """, (user_id, period_start))

                by_model = {row['model']: row['tokens'] for row in cur.fetchall()}

                return {
                    'user_id': user_id,
                    'total_tokens': totals['total_tokens'],
                    'total_cost_eur': float(totals['total_cost_eur']),
                    'total_requests': totals['total_requests'],
                    'by_method': by_method,
                    'by_provider': by_provider,
                    'by_model': by_model,
                    'period_start': period_start,
                    'period_end': datetime.now()
                }

    @classmethod
    def get_lesson_executions(
        cls,
        user_id: str,
        lesson_id: str,
        method_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get execution history for a lesson.

        Args:
            user_id: User ID
            lesson_id: Lesson ID
            method_id: Optional filter by method
            limit: Maximum results (default 50)

        Returns:
            List of execution records with method info
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                if method_id:
                    cur.execute("""
                        SELECT
                            e.execution_id,
                            e.method_id,
                            e.user_input,
                            e.output_text as ai_response,
                            e.input_tokens,
                            e.output_tokens,
                            e.total_tokens,
                            e.model,
                            e.provider,
                            e.executed_at,
                            m.title as method_name,
                            m.instructions as method_description
                        FROM learning_method_executions e
                        JOIN learning_methods m ON e.method_id = m.method_id
                        WHERE e.user_id = %s
                          AND e.lesson_id = %s
                          AND e.method_id = %s
                        ORDER BY e.executed_at DESC
                        LIMIT %s
                    """, (user_id, lesson_id, method_id, limit))
                else:
                    cur.execute("""
                        SELECT
                            e.execution_id,
                            e.method_id,
                            e.user_input,
                            e.output_text as ai_response,
                            e.input_tokens,
                            e.output_tokens,
                            e.total_tokens,
                            e.model,
                            e.provider,
                            e.executed_at,
                            m.title as method_name,
                            m.instructions as method_description
                        FROM learning_method_executions e
                        JOIN learning_methods m ON e.method_id = m.method_id
                        WHERE e.user_id = %s
                          AND e.lesson_id = %s
                        ORDER BY e.executed_at DESC
                        LIMIT %s
                    """, (user_id, lesson_id, limit))

                executions = cur.fetchall()

                # Convert IDs and timestamps to strings for JSON serialization
                for exec_record in executions:
                    exec_record['execution_id'] = str(exec_record['execution_id'])
                    exec_record['method_id'] = str(exec_record['method_id'])
                    if exec_record['executed_at']:
                        exec_record['executed_at'] = exec_record['executed_at'].isoformat()

                return executions

    @classmethod
    def delete_execution(cls, execution_id: str, user_id: str) -> bool:
        """
        Delete an execution record (ownership check).

        Args:
            execution_id: Execution UUID
            user_id: User UUID (must be owner)

        Returns:
            True if deleted, False if not found or not owned
        """
        with db_pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM learning_method_executions
                    WHERE execution_id = %s AND user_id = %s
                    RETURNING execution_id
                """, (execution_id, user_id))

                result = cur.fetchone()
                conn.commit()
                return result is not None

    @classmethod
    def get_statistics(cls) -> Dict[str, Any]:
        """
        Get overall learning method statistics.

        Returns:
            {
                'total_methods': int,
                'active_methods': int,
                'by_tier': {tier: count},
                'ai_powered_count': int,
                'most_used': str | None,
                'total_executions': int,
                'total_tokens': int,
                'total_cost_eur': float
            }
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Get method counts
                cur.execute("""
                    SELECT
                        COUNT(*) as total_methods,
                        SUM(CASE WHEN published = TRUE THEN 1 ELSE 0 END) as active_methods,
                        SUM(CASE WHEN data->>'ai_enabled' = 'true' THEN 1 ELSE 0 END) as ai_powered_count
                    FROM learning_methods
                """)

                method_stats = cur.fetchone()

                # Get distribution by tier
                cur.execute("""
                    SELECT tier, COUNT(*) as count
                    FROM learning_methods
                    GROUP BY tier
                    ORDER BY tier
                """)

                by_tier = {row['tier']: row['count'] for row in cur.fetchall()}

                # Most used method (from executions)
                cur.execute("""
                    SELECT
                        m.title as method_name,
                        COUNT(e.execution_id) as execution_count
                    FROM learning_method_executions e
                    JOIN learning_methods m ON e.method_id = m.method_id
                    GROUP BY e.method_id, m.title
                    ORDER BY execution_count DESC
                    LIMIT 1
                """)

                most_used_row = cur.fetchone()
                most_used = most_used_row['method_name'] if most_used_row else None

                # Get execution and token stats
                cur.execute("""
                    SELECT
                        COUNT(*) as total_executions,
                        COALESCE(SUM(total_tokens), 0) as total_tokens,
                        COALESCE(SUM(cost_eur), 0) as total_cost_eur
                    FROM learning_method_executions
                """)

                exec_stats = cur.fetchone()

                return {
                    'total_methods': method_stats['total_methods'],
                    'active_methods': method_stats['active_methods'],
                    'by_tier': by_tier,
                    'ai_powered_count': method_stats['ai_powered_count'] or 0,
                    'most_used': most_used,
                    'total_executions': exec_stats['total_executions'],
                    'total_tokens': exec_stats['total_tokens'],
                    'total_cost_eur': float(exec_stats['total_cost_eur'] or 0.0)
                }
