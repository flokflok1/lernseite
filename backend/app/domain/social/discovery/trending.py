"""Trending Content Discovery"""

from typing import List, Dict, Any
from app.infrastructure.persistence.repositories.base_repository import BaseRepository


class TrendingService:
    """Discover trending posts, users, hashtags"""
    
    @staticmethod
    def get_trending_posts(limit: int = 20) -> List[Dict[str, Any]]:
        """Get trending posts (last 24h, high engagement)"""
        query = """
            SELECT p.*, u.username,
                   (p.likes_count + 2 * p.comments_count + 3 * p.shares_count) as engagement_score
            FROM social.social_posts p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
              AND p.visibility = 'public'
              AND p.moderation_status = 'ai_approved'
            ORDER BY engagement_score DESC, p.created_at DESC
            LIMIT %s
        """
        return BaseRepository.fetch_all(query, (limit,))
