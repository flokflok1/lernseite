"""Trending Content Discovery"""

from typing import List, Dict, Any
from app.domain.ports.core.registry import repos


class TrendingService:
    """Discover trending posts, users, hashtags"""

    @staticmethod
    def get_trending_posts(limit: int = 20) -> List[Dict[str, Any]]:
        """Get trending posts (last 24h, high engagement)"""
        return repos.social_posts.get_trending_posts(limit)
