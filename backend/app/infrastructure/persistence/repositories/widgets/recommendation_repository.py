"""
LernsystemX KI Recommendations Repository

Handles ki_recommendations table operations:
- Create KI recommendations
- Get recommendations for user
- Mark as shown/dismissed/accepted
- Clean expired recommendations

Pure psycopg3 - No ORM
"""

from typing import Optional, List, Dict
from datetime import datetime, timedelta
import json

from app.infrastructure.persistence.repositories.base_repository import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query, insert_returning, update_returning


class RecommendationRepository(BaseRepository):
    """
    KI Recommendations repository

    Manages AI-generated recommendations for Premium+ users
    """

    table_name = 'ki_recommendations'
    pk_column = 'recommendation_id'

    @classmethod
    def create_recommendation(
        cls,
        user_id: str,
        recommendation_type: str,
        target_type: str,
        target_id: str,
        score: float,
        reason: str,
        confidence: float = 0.85,
        context: Optional[Dict] = None,
        ttl_days: int = 7
    ) -> Dict:
        """
        Create new KI recommendation

        Args:
            user_id: User UUID
            recommendation_type: Type (course, module, method, etc.)
            target_type: Target type
            target_id: Target UUID
            score: Recommendation score (0.0-1.0)
            reason: Reason for recommendation (KI-generated)
            confidence: Confidence score
            context: Optional context dict
            ttl_days: TTL in days

        Returns:
            Created recommendation dict
        """
        query = """
            INSERT INTO ki_recommendations (
                user_id,
                recommendation_type,
                target_type,
                target_id,
                score,
                confidence,
                reason,
                context,
                is_shown,
                is_dismissed,
                is_accepted,
                created_at,
                expires_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, FALSE, FALSE, FALSE, %s, %s)
            RETURNING *
        """

        now = datetime.utcnow()
        expires_at = now + timedelta(days=ttl_days)

        result = insert_returning(
            query,
            (
                user_id,
                recommendation_type,
                target_type,
                target_id,
                score,
                confidence,
                reason,
                json.dumps(context or {}),
                now,
                expires_at
            )
        )

        if result and isinstance(result.get('context'), str):
            result['context'] = json.loads(result['context'])

        return result

    @classmethod
    def get_recommendations(
        cls,
        user_id: str,
        limit: int = 10,
        include_dismissed: bool = False
    ) -> List[Dict]:
        """
        Get recommendations for user

        Args:
            user_id: User UUID
            limit: Max recommendations
            include_dismissed: Include dismissed recommendations

        Returns:
            List of recommendation dicts
        """
        if include_dismissed:
            query = """
                SELECT *
                FROM ki_recommendations
                WHERE user_id = %s
                  AND expires_at > NOW()
                ORDER BY score DESC, created_at DESC
                LIMIT %s
            """
        else:
            query = """
                SELECT *
                FROM ki_recommendations
                WHERE user_id = %s
                  AND is_dismissed = FALSE
                  AND expires_at > NOW()
                ORDER BY score DESC, created_at DESC
                LIMIT %s
            """

        results = fetch_all(query, (user_id, limit))

        # Parse JSONB context
        for result in results:
            if isinstance(result.get('context'), str):
                result['context'] = json.loads(result['context'])

        return results

    @classmethod
    def mark_as_shown(cls, recommendation_id: str) -> bool:
        """
        Mark recommendation as shown

        Args:
            recommendation_id: Recommendation UUID

        Returns:
            bool: Success
        """
        query = """
            UPDATE ki_recommendations
            SET is_shown = TRUE,
                shown_at = %s
            WHERE recommendation_id = %s
              AND is_shown = FALSE
        """

        rows_affected = execute_query(query, (datetime.utcnow(), recommendation_id))
        return rows_affected > 0

    @classmethod
    def mark_as_dismissed(cls, recommendation_id: str) -> bool:
        """
        Mark recommendation as dismissed

        Args:
            recommendation_id: Recommendation UUID

        Returns:
            bool: Success
        """
        query = """
            UPDATE ki_recommendations
            SET is_dismissed = TRUE,
                dismissed_at = %s
            WHERE recommendation_id = %s
        """

        rows_affected = execute_query(query, (datetime.utcnow(), recommendation_id))
        return rows_affected > 0

    @classmethod
    def mark_as_accepted(cls, recommendation_id: str) -> bool:
        """
        Mark recommendation as accepted

        Args:
            recommendation_id: Recommendation UUID

        Returns:
            bool: Success
        """
        query = """
            UPDATE ki_recommendations
            SET is_accepted = TRUE,
                accepted_at = %s
            WHERE recommendation_id = %s
        """

        rows_affected = execute_query(query, (datetime.utcnow(), recommendation_id))
        return rows_affected > 0

    @classmethod
    def get_recommendation_stats(cls, user_id: str) -> Dict:
        """
        Get recommendation statistics for user

        Args:
            user_id: User UUID

        Returns:
            Dict with stats
        """
        query = """
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE is_shown = TRUE) as shown,
                COUNT(*) FILTER (WHERE is_dismissed = TRUE) as dismissed,
                COUNT(*) FILTER (WHERE is_accepted = TRUE) as accepted,
                AVG(score) as avg_score,
                AVG(confidence) as avg_confidence
            FROM ki_recommendations
            WHERE user_id = %s
              AND expires_at > NOW()
        """

        return fetch_one(query, (user_id,))

    @classmethod
    def clean_expired(cls) -> int:
        """
        Clean expired recommendations

        Uses PostgreSQL function: cleanup_expired_recommendations()

        Returns:
            int: Number of deleted recommendations
        """
        query = "SELECT cleanup_expired_recommendations()"
        result = fetch_one(query)
        return result['cleanup_expired_recommendations'] if result else 0
