"""Hashtag System"""

from typing import List, Dict, Any
from app.domain.ports.core.registry import repos


class HashtagService:
    """Hashtag discovery and tracking"""

    @staticmethod
    def get_trending_hashtags(limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending hashtags"""
        return repos.social_posts.get_trending_hashtags(limit)
