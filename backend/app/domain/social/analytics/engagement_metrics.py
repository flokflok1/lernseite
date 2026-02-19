"""Engagement Metrics (Likes, Comments, Shares)"""

from typing import Dict, Any
from app.domain.ports.core.registry import repos


class EngagementMetrics:
    """Track engagement metrics"""

    @staticmethod
    def get_post_metrics(post_id: str) -> Dict[str, Any]:
        """Get engagement metrics for post"""
        return repos.social_posts.get_post_metrics(post_id)
