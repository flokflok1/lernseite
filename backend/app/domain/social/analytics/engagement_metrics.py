"""Engagement Metrics (Likes, Comments, Shares)"""

from typing import Dict, Any
from app.domain.ports.registry import repos


class EngagementMetrics:
    """Track engagement metrics"""

    @staticmethod
    def get_post_metrics(post_id: str) -> Dict[str, Any]:
        """Get engagement metrics for post"""
        query = """
            SELECT
                likes_count,
                comments_count,
                shares_count,
                views_count
            FROM social.social_posts
            WHERE post_id = %s
        """
        return repos.query_runner.fetch_one(query, (post_id,)) or {}
