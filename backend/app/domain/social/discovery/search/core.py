"""Full-Text Search"""

from typing import List, Dict, Any
from app.domain.ports.core.registry import repos


class SearchService:
    """Search posts, users, hashtags"""
    
    @staticmethod
    def search_posts(query_text: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search posts by content"""
        query = """
            SELECT p.*, u.username
            FROM social.social_posts p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.content ILIKE %s
              AND p.visibility = 'public'
            ORDER BY p.created_at DESC
            LIMIT %s
        """
        return repos.query_runner.fetch_all(query, (f'%{query_text}%', limit))
