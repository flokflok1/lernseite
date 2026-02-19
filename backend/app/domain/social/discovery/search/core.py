"""Full-Text Search"""

from typing import List, Dict, Any
from app.domain.ports.core.registry import repos


class SearchService:
    """Search posts, users, hashtags"""

    @staticmethod
    def search_posts(query_text: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search posts by content"""
        return repos.social_posts.search_posts_by_content(query_text, limit)
