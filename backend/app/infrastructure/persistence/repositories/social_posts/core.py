"""
Social Posts Repository

Database operations for social_posts table
"""

from typing import Optional, Dict, List
from app.infrastructure.persistence.repositories.core.base import BaseRepository


class SocialPostsCoreRepository(BaseRepository):
    """Repository for social_posts CRUD operations"""

    @staticmethod
    def create(data: Dict) -> Dict:
        """Create new post"""
        query = """
        INSERT INTO social_posts (user_id, content, content_type, visibility, moderation_status)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING post_id, user_id, content, content_type, visibility, created_at
        """
        return SocialPostsCoreRepository.fetch_one(query, (
            data['user_id'],
            data['content'],
            data['content_type'],
            data['visibility'],
            data.get('moderation_status', 'pending')
        ))

    @staticmethod
    def get_by_id(post_id: str) -> Optional[Dict]:
        """Get post by ID"""
        query = """
        SELECT * FROM social_posts
        WHERE post_id = %s AND deleted_at IS NULL
        """
        return SocialPostsCoreRepository.fetch_one(query, (post_id,))

    @staticmethod
    def update(post_id: str, data: Dict) -> Optional[Dict]:
        """Update post"""
        set_clauses = []
        params = []
        for key, value in data.items():
            set_clauses.append(f"{key} = %s")
            params.append(value)
        
        params.append(post_id)
        query = f"""
        UPDATE social_posts SET {', '.join(set_clauses)}
        WHERE post_id = %s
        RETURNING *
        """
        return SocialPostsCoreRepository.fetch_one(query, tuple(params))

    @staticmethod
    def soft_delete(post_id: str) -> bool:
        """Soft delete post"""
        query = """
        UPDATE social_posts SET deleted_at = CURRENT_TIMESTAMP
        WHERE post_id = %s
        """
        SocialPostsCoreRepository.execute(query, (post_id,))
        return True

    @staticmethod
    def get_user_posts(user_id: str, viewer_user_id: str, page: int, per_page: int) -> Dict:
        """Get user posts with pagination"""
        offset = (page - 1) * per_page
        query = """
        SELECT * FROM social_posts
        WHERE user_id = %s AND deleted_at IS NULL
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """
        posts = SocialPostsCoreRepository.fetch_all(query, (user_id, per_page, offset))
        return {'posts': posts, 'page': page, 'per_page': per_page}

    @staticmethod
    def pin(post_id: str) -> bool:
        """Pin post"""
        query = "UPDATE social_posts SET is_pinned = TRUE WHERE post_id = %s"
        SocialPostsCoreRepository.execute(query, (post_id,))
        return True

    @staticmethod
    def unpin_all_for_user(user_id: str):
        """Unpin all posts for user"""
        query = "UPDATE social_posts SET is_pinned = FALSE WHERE user_id = %s"
        SocialPostsCoreRepository.execute(query, (user_id,))

    @staticmethod
    def add_mention(post_id: str, mentioned_user_id: str):
        """Add mention"""
        query = """
        INSERT INTO social_post_mentions (post_id, mentioned_user_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
        """
        SocialPostsCoreRepository.execute(query, (post_id, mentioned_user_id))

    @staticmethod
    def add_hashtag(post_id: str, hashtag: str):
        """Add hashtag"""
        query = """
        INSERT INTO social_post_hashtags (post_id, hashtag)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
        """
        SocialPostsCoreRepository.execute(query, (post_id, hashtag))
