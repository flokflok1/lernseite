"""Hashtag System"""

from typing import List, Dict, Any
from app.domain.ports.registry import repos


class HashtagService:
    """Hashtag discovery and tracking"""
    
    @staticmethod
    def get_trending_hashtags(limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending hashtags"""
        query = """
            SELECT hashtag, COUNT(*) as post_count
            FROM social.social_post_hashtags
            WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
            GROUP BY hashtag
            ORDER BY post_count DESC
            LIMIT %s
        """
        return repos.query_runner.fetch_all(query, (limit,))
