"""
AI Usage Statistics Repository

Handles AI usage statistics and analytics from ki_requests and ai_usage_aggregates tables.

Phase B24-05 - AI Pipeline Analytics
ISO 27001:2013 compliant - Usage tracking and billing
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all


class AIUsageRepository:
    """
    Repository for AI usage statistics and analytics.

    Handles:
    - Token usage statistics
    - Cost analytics
    - Provider/model breakdown
    - Time-based aggregation
    """

    @classmethod
    def get_usage_stats(
        cls,
        period: str = 'month',
        user_id: Optional[str] = None,
        organisation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get AI usage statistics for a given period.

        Args:
            period: Time period ('day', 'week', 'month', 'year')
            user_id: Filter by user ID (optional)
            organisation_id: Filter by organisation ID (optional)

        Returns:
            Dict with usage statistics:
            - total_requests: Total number of AI requests
            - total_tokens: Total tokens used (input + output)
            - total_cost: Total cost in USD
            - by_provider: Breakdown by AI provider
            - by_model: Breakdown by AI model
            - by_request_type: Breakdown by request type
        """
        # Calculate date range based on period
        end_date = datetime.now()
        if period == 'day':
            start_date = end_date - timedelta(days=1)
        elif period == 'week':
            start_date = end_date - timedelta(weeks=1)
        elif period == 'month':
            start_date = end_date - timedelta(days=30)
        elif period == 'year':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)  # Default to month

        # Build WHERE clause
        where_clauses = ["k.created_at >= %s", "k.created_at <= %s"]
        params = [start_date, end_date]

        if user_id:
            where_clauses.append("k.user_id = %s")
            params.append(user_id)

        if organisation_id:
            where_clauses.append("k.organisation_id = %s")
            params.append(organisation_id)

        where_sql = " AND ".join(where_clauses)

        # Get overall stats
        overall_query = f"""
            SELECT
                COUNT(*) as total_requests,
                COALESCE(SUM(k.tokens_total), 0) as total_tokens,
                COALESCE(SUM(k.tokens_input), 0) as total_tokens_input,
                COALESCE(SUM(k.tokens_output), 0) as total_tokens_output,
                COALESCE(SUM(k.cost_usd), 0) as total_cost,
                COUNT(*) FILTER (WHERE k.status = 'completed') as successful_requests,
                COUNT(*) FILTER (WHERE k.status = 'failed') as failed_requests,
                AVG(k.processing_time_ms) as avg_processing_time_ms
            FROM ai_pipeline.ki_requests k
            WHERE {where_sql}
        """

        overall_stats = fetch_one(overall_query, tuple(params))

        # Get breakdown by provider
        provider_query = f"""
            SELECT
                p.name as provider,
                COUNT(*) as request_count,
                COALESCE(SUM(k.tokens_total), 0) as total_tokens,
                COALESCE(SUM(k.cost_usd), 0) as total_cost
            FROM ai_pipeline.ki_requests k
            LEFT JOIN ai_pipeline.ai_models m ON k.model_id = m.model_id
            LEFT JOIN ai_pipeline.ai_providers p ON m.provider_id = p.provider_id
            WHERE {where_sql}
            GROUP BY p.name
            ORDER BY total_cost DESC
        """

        by_provider = fetch_all(provider_query, tuple(params)) or []

        # Get breakdown by model
        model_query = f"""
            SELECT
                k.model_used,
                p.name as provider,
                COUNT(*) as request_count,
                COALESCE(SUM(k.tokens_total), 0) as total_tokens,
                COALESCE(SUM(k.cost_usd), 0) as total_cost
            FROM ai_pipeline.ki_requests k
            LEFT JOIN ai_pipeline.ai_models m ON k.model_id = m.model_id
            LEFT JOIN ai_pipeline.ai_providers p ON m.provider_id = p.provider_id
            WHERE {where_sql}
            GROUP BY k.model_used, p.name
            ORDER BY total_cost DESC
            LIMIT 10
        """

        by_model = fetch_all(model_query, tuple(params)) or []

        # Get breakdown by request type
        request_type_query = f"""
            SELECT
                k.request_type,
                COUNT(*) as request_count,
                COALESCE(SUM(k.tokens_total), 0) as total_tokens,
                COALESCE(SUM(k.cost_usd), 0) as total_cost
            FROM ai_pipeline.ki_requests k
            WHERE {where_sql}
            GROUP BY k.request_type
            ORDER BY request_count DESC
        """

        by_request_type = fetch_all(request_type_query, tuple(params)) or []

        return {
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_requests': overall_stats.get('total_requests', 0) if overall_stats else 0,
            'total_tokens': overall_stats.get('total_tokens', 0) if overall_stats else 0,
            'total_tokens_input': overall_stats.get('total_tokens_input', 0) if overall_stats else 0,
            'total_tokens_output': overall_stats.get('total_tokens_output', 0) if overall_stats else 0,
            'total_cost': float(overall_stats.get('total_cost', 0)) if overall_stats else 0.0,
            'successful_requests': overall_stats.get('successful_requests', 0) if overall_stats else 0,
            'failed_requests': overall_stats.get('failed_requests', 0) if overall_stats else 0,
            'avg_processing_time_ms': float(overall_stats.get('avg_processing_time_ms', 0)) if overall_stats and overall_stats.get('avg_processing_time_ms') else 0.0,
            'by_provider': [dict(row) for row in by_provider],
            'by_model': [dict(row) for row in by_model],
            'by_request_type': [dict(row) for row in by_request_type]
        }

    @classmethod
    def get_daily_usage(
        cls,
        days: int = 30,
        user_id: Optional[str] = None,
        organisation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get daily usage statistics for the last N days.

        Args:
            days: Number of days to retrieve (default: 30)
            user_id: Filter by user ID (optional)
            organisation_id: Filter by organisation ID (optional)

        Returns:
            List of daily usage stats
        """
        where_clauses = ["date >= CURRENT_DATE - INTERVAL '%s days'"]
        params = [days]

        if user_id:
            where_clauses.append("user_id = %s")
            params.append(user_id)

        if organisation_id:
            where_clauses.append("organisation_id = %s")
            params.append(organisation_id)

        where_sql = " AND ".join(where_clauses)

        query = f"""
            SELECT
                date,
                COALESCE(SUM(request_count), 0) as request_count,
                COALESCE(SUM(total_tokens), 0) as total_tokens,
                COALESCE(SUM(total_cost_usd), 0) as total_cost
            FROM ai_pipeline.ai_usage_aggregates
            WHERE {where_sql}
            GROUP BY date
            ORDER BY date DESC
        """

        results = fetch_all(query, tuple(params))

        return [
            {
                'date': row['date'].isoformat() if row['date'] else None,
                'request_count': row['request_count'],
                'total_tokens': row['total_tokens'],
                'total_cost': float(row['total_cost'])
            }
            for row in (results or [])
        ]

    @classmethod
    def get_top_users(
        cls,
        period_days: int = 30,
        limit: int = 10,
        organisation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get top users by AI usage.

        Args:
            period_days: Period in days
            limit: Number of top users to return
            organisation_id: Filter by organisation (optional)

        Returns:
            List of top users with usage stats
        """
        where_clauses = ["k.created_at >= CURRENT_DATE - INTERVAL '%s days'"]
        params = [period_days]

        if organisation_id:
            where_clauses.append("k.organisation_id = %s")
            params.append(organisation_id)

        where_sql = " AND ".join(where_clauses)
        params.append(limit)

        query = f"""
            SELECT
                u.user_id,
                u.email,
                u.username,
                COUNT(*) as request_count,
                COALESCE(SUM(k.tokens_total), 0) as total_tokens,
                COALESCE(SUM(k.cost_usd), 0) as total_cost
            FROM ai_pipeline.ki_requests k
            JOIN core.users u ON k.user_id = u.user_id
            WHERE {where_sql}
            GROUP BY u.user_id, u.email, u.username
            ORDER BY total_cost DESC
            LIMIT %s
        """

        results = fetch_all(query, tuple(params))

        return [
            {
                'user_id': row['user_id'],
                'email': row['email'],
                'username': row['username'],
                'request_count': row['request_count'],
                'total_tokens': row['total_tokens'],
                'total_cost': float(row['total_cost'])
            }
            for row in (results or [])
        ]
