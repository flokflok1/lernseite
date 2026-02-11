"""Explore Page - Discover New Content"""

from typing import List, Dict, Any
from app.domain.ports.core.registry import repos


class ExploreService:
    """Explore content outside user's network"""
    
    @staticmethod
    def get_explore_feed(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get explore feed (public posts from users not followed)"""
        query = """
            SELECT p.*, u.username
            FROM social.social_posts p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.user_id NOT IN (
                SELECT following_id FROM social.social_follows WHERE follower_id = %s
            )
            AND p.visibility = 'public'
            AND p.moderation_status = 'ai_approved'
            ORDER BY p.created_at DESC
            LIMIT %s
        """
        return repos.query_runner.fetch_all(query, (user_id, limit))
