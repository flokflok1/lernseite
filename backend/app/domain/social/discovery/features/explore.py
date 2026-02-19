"""Explore Page - Discover New Content"""

from typing import List, Dict, Any
from app.domain.ports.core.registry import repos


class ExploreService:
    """Explore content outside user's network"""

    @staticmethod
    def get_explore_feed(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get explore feed (public posts from users not followed)"""
        return repos.social_posts.get_explore_posts(user_id, limit)
