"""
Agent Query Logging and Analytics

Handles query tracking and analytics:
- Query logging with performance metrics
- Query feedback collection
- Query statistics and aggregation
- Popular query trending

Inherits from BaseRepository for connection pooling and standard operations.
"""

from typing import Optional, Dict, List, Any
import hashlib

from app.infrastructure.persistence.repositories.core.base import BaseRepository


class KnowledgeRepositoryQueryLog(BaseRepository):
    """
    Query logging and analytics for Agent interactions

    Handles query tracking including:
    - Logging agent queries with performance metrics
    - Recording user feedback on responses
    - Aggregating statistics across time periods
    - Identifying popular queries
    """

    table_name = 'smart_agents.agent_query_log'

    @staticmethod
    def log_query(
        agent_id: str,
        user_id: str,
        query_text: str,
        response_source: str,
        response_text: Optional[str] = None,
        cache_key: Optional[str] = None,
        tokens_used: int = 0,
        tokens_saved: int = 0,
        cost_eur: float = 0,
        latency_ms: Optional[int] = None,
        ai_provider: Optional[str] = None,
        ai_model: Optional[str] = None,
        was_offline_mode: bool = False,
        context_scope: Optional[str] = None,
        context_id: Optional[str] = None,
        method_type: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Log an agent query with performance metrics

        Args:
            agent_id: Agent UUID
            user_id: User UUID
            query_text: Question asked
            response_source: Source of response (cache_hit, ai_generated, etc.)
            response_text: Optional response text
            cache_key: Optional cache key used
            tokens_used: Tokens consumed
            tokens_saved: Tokens saved (if cache hit)
            cost_eur: Cost in EUR
            latency_ms: Response latency in milliseconds
            ai_provider: AI provider used (anthropic, openai, etc.)
            ai_model: AI model used
            was_offline_mode: Whether in offline mode
            context_scope: Optional context scope (course, chapter, lesson)
            context_id: Optional context ID
            method_type: Optional learning method type (0-11)

        Returns:
            Created query log entry
        """
        query_hash = hashlib.sha256(
            query_text.lower().strip().encode()
        ).hexdigest()

        query = """
            INSERT INTO smart_agents.agent_query_log (
                agent_id,
                user_id,
                query_text,
                query_hash,
                context_scope,
                context_id,
                method_type,
                response_text,
                response_source,
                cache_key,
                tokens_used,
                tokens_saved,
                cost_eur,
                latency_ms,
                ai_provider,
                ai_model,
                was_offline_mode
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING *
        """
        return KnowledgeRepositoryQueryLog.fetch_one(query, (
            agent_id,
            user_id,
            query_text,
            query_hash,
            context_scope,
            context_id,
            method_type,
            response_text,
            response_source,
            cache_key,
            tokens_used,
            tokens_saved,
            cost_eur,
            latency_ms,
            ai_provider,
            ai_model,
            was_offline_mode
        ))

    @staticmethod
    def get_query_by_id(query_id: str) -> Optional[Dict[str, Any]]:
        """
        Get query log entry by ID

        Args:
            query_id: Query UUID

        Returns:
            Query log data or None
        """
        query = """
            SELECT *
            FROM smart_agents.agent_query_log
            WHERE query_id = %s
        """
        return KnowledgeRepositoryQueryLog.fetch_one(query, (query_id,))

    @staticmethod
    def update_query_feedback(
        query_id: str,
        rating: Optional[int] = None,
        feedback: Optional[str] = None,
        was_helpful: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update query with user feedback

        Args:
            query_id: Query UUID
            rating: 1-5 rating scale
            feedback: Text feedback from user
            was_helpful: Boolean helpful indicator

        Returns:
            Updated query data or None if no updates
        """
        updates = []
        params: List[Any] = []

        if rating is not None:
            updates.append("user_rating = %s")
            params.append(rating)

        if feedback is not None:
            updates.append("user_feedback = %s")
            params.append(feedback)

        if was_helpful is not None:
            updates.append("was_helpful = %s")
            params.append(was_helpful)

        if not updates:
            return None

        set_clause = ", ".join(updates)
        query = f"""
            UPDATE smart_agents.agent_query_log
            SET {set_clause}
            WHERE query_id = %s
            RETURNING *
        """
        params.append(query_id)
        return KnowledgeRepositoryQueryLog.fetch_one(query, tuple(params))

    @staticmethod
    def get_query_stats(
        agent_id: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get query statistics for an agent over time period

        Args:
            agent_id: Agent UUID
            days: Number of days to look back (default 7)

        Returns:
            Statistics dictionary with aggregated metrics:
            - total_queries: Total number of queries
            - cache_hits: Number of cache hit responses
            - ai_generated: Number of AI-generated responses
            - offline_queries: Number of offline mode queries
            - total_tokens_used: Total tokens consumed
            - total_tokens_saved: Total tokens saved via caching
            - total_cost_eur: Total cost in EUR
            - avg_latency_ms: Average response latency
            - avg_rating: Average user rating
        """
        query = """
            SELECT
                COUNT(*) as total_queries,
                COUNT(*) FILTER (WHERE response_source = 'cache_hit') as cache_hits,
                COUNT(*) FILTER (WHERE response_source = 'ai_generated') as ai_generated,
                COUNT(*) FILTER (WHERE was_offline_mode = TRUE) as offline_queries,
                SUM(tokens_used) as total_tokens_used,
                SUM(tokens_saved) as total_tokens_saved,
                SUM(cost_eur) as total_cost_eur,
                AVG(latency_ms) as avg_latency_ms,
                AVG(user_rating) FILTER (WHERE user_rating IS NOT NULL) as avg_rating
            FROM smart_agents.agent_query_log
            WHERE agent_id = %s
            AND created_at > NOW() - INTERVAL '%s days'
        """
        return KnowledgeRepositoryQueryLog.fetch_one(query, (agent_id, days))

    @staticmethod
    def get_popular_queries(
        agent_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get most popular queries for an agent

        Groups identical questions by hash and returns aggregated metrics.

        Args:
            agent_id: Agent UUID
            limit: Max results (default 10)

        Returns:
            List of popular queries ordered by frequency with metrics:
            - query_hash: SHA256 hash of question
            - query_text: Original question text
            - query_count: Number of times asked
            - avg_rating: Average user rating
        """
        query = """
            SELECT
                query_hash,
                MIN(query_text) as query_text,
                COUNT(*) as query_count,
                AVG(user_rating) FILTER (WHERE user_rating IS NOT NULL) as avg_rating
            FROM smart_agents.agent_query_log
            WHERE agent_id = %s
            GROUP BY query_hash
            ORDER BY query_count DESC
            LIMIT %s
        """
        return KnowledgeRepositoryQueryLog.fetch_all(query, (agent_id, limit))
