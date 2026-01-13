"""
LernsystemX - Authoring Action Analytics

Database operations for tracking usage statistics and analytics
of authoring actions in KI-Studio.
"""

from typing import Optional, List, Dict, Any
import logging
import json

from app.repositories.base_repository import BaseRepository
from app.database.connection import fetch_one, fetch_all

logger = logging.getLogger(__name__)


class AuthoringActionAnalytics(BaseRepository):
    """
    Analytics operations for authoring actions.

    Tracks usage statistics, popular actions, and cost metrics
    for actions used in KI-Studio.
    """

    table_name = 'learning_methods.authoring_action_usage'
    pk_column = 'usage_id'

    @staticmethod
    def log_usage(
        action_id: str,
        user_id: str,
        session_id: str = None,
        context_data: Dict = None,
        was_successful: bool = True,
        was_confirmed: bool = None,
        result_entity_id: str = None,
        tokens_input: int = None,
        tokens_output: int = None,
        cost_eur: float = None,
        response_time_ms: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Log action usage for analytics.

        Records usage metrics including success status, tokens used,
        cost, and response time.

        Args:
            action_id: Action UUID used
            user_id: User ID who used the action
            session_id: Optional authoring session ID for grouping
            context_data: Optional dict of context when action was triggered
            was_successful: Whether the action execution succeeded
            was_confirmed: Whether user confirmed (if confirmation required)
            result_entity_id: ID of entity created/modified by action
            tokens_input: Input tokens consumed
            tokens_output: Output tokens generated
            cost_eur: Total cost in EUR (if applicable)
            response_time_ms: Time to generate response (milliseconds)

        Returns:
            Usage record dict with usage_id or None if insert failed
        """
        tokens_total = None
        if tokens_input is not None and tokens_output is not None:
            tokens_total = tokens_input + tokens_output

        context_json = json.dumps(context_data) if context_data else None

        query = """
            INSERT INTO authoring_action_usage (
                action_id, user_id, session_id, context_data,
                was_successful, was_confirmed, result_entity_id,
                tokens_input, tokens_output, tokens_total,
                cost_eur, response_time_ms
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s
            )
            RETURNING usage_id
        """
        return fetch_one(query, (
            action_id, user_id, session_id, context_json,
            was_successful, was_confirmed, result_entity_id,
            tokens_input, tokens_output, tokens_total,
            cost_eur, response_time_ms
        ))

    @staticmethod
    def get_usage_stats(action_id: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Get usage statistics for an action or all actions.

        Returns aggregated metrics over a time window.

        Args:
            action_id: Optional action UUID to filter by. If None, returns system-wide stats
            days: Number of days to look back (default: 30)

        Returns:
            Dict with keys:
                - total_uses: Total number of times action was used
                - successful_uses: Count of successful executions
                - confirmed_uses: Count of confirmed executions
                - total_tokens: Sum of all tokens used
                - total_cost: Sum of all costs in EUR
                - avg_response_time: Average response time in milliseconds
                - actions_used: (global stats only) Count of distinct actions
                - unique_users: (global stats only) Count of distinct users
        """
        if action_id:
            query = """
                SELECT
                    COUNT(*) as total_uses,
                    COUNT(CASE WHEN was_successful THEN 1 END) as successful_uses,
                    COUNT(CASE WHEN was_confirmed THEN 1 END) as confirmed_uses,
                    SUM(tokens_total) as total_tokens,
                    SUM(cost_eur) as total_cost,
                    AVG(response_time_ms) as avg_response_time
                FROM authoring_action_usage
                WHERE action_id = %s
                  AND created_at >= NOW() - INTERVAL '%s days'
            """
            result = fetch_one(query, (action_id, days))
        else:
            query = """
                SELECT
                    COUNT(*) as total_uses,
                    COUNT(CASE WHEN was_successful THEN 1 END) as successful_uses,
                    COUNT(CASE WHEN was_confirmed THEN 1 END) as confirmed_uses,
                    SUM(tokens_total) as total_tokens,
                    SUM(cost_eur) as total_cost,
                    AVG(response_time_ms) as avg_response_time,
                    COUNT(DISTINCT action_id) as actions_used,
                    COUNT(DISTINCT user_id) as unique_users
                FROM authoring_action_usage
                WHERE created_at >= NOW() - INTERVAL '%s days'
            """
            result = fetch_one(query, (days,))

        return result or {}

    @staticmethod
    def get_popular_actions(limit: int = 10, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get most popular actions by usage count.

        Returns actions with the highest usage counts over a time window.

        Args:
            limit: Maximum number of actions to return (default: 10)
            days: Number of days to look back (default: 30)

        Returns:
            List of dicts with keys:
                - action_id: Action UUID
                - action_key: Action key identifier
                - category: Action category
                - label: Human-readable label
                - icon: Icon identifier
                - usage_count: Total number of uses
                - success_count: Count of successful uses
        """
        query = """
            SELECT
                a.action_id, a.action_key, a.category, a.label, a.icon,
                COUNT(u.usage_id) as usage_count,
                COUNT(CASE WHEN u.was_successful THEN 1 END) as success_count
            FROM learning_methods.authoring_actions a
            LEFT JOIN authoring_action_usage u ON a.action_id = u.action_id
                AND u.created_at >= NOW() - INTERVAL '%s days'
            WHERE a.is_active = true
            GROUP BY a.action_id, a.action_key, a.category, a.label, a.icon
            ORDER BY usage_count DESC
            LIMIT %s
        """
        return fetch_all(query, (days, limit))
