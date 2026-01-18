"""
Social Likes Repository

Handles database operations for likes, reactions, shares, and bookmarks.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from app.infrastructure.persistence.repositories.base_repository import BaseRepository


class SocialLikesRepository(BaseRepository):
    """Repository for social_likes and engagement tables"""

    # =====================
    # LIKES
    # =====================

    @staticmethod
    def create_like(user_id: str, post_id: str) -> Optional[Dict[str, Any]]:
        """
        Like a post.

        Args:
            user_id: User ID who likes
            post_id: Post ID being liked

        Returns:
            Created like record or None
        """
        query = """
            INSERT INTO social.social_likes (user_id, post_id)
            VALUES (%s, %s)
            ON CONFLICT (user_id, post_id) DO NOTHING
            RETURNING *
        """
        return SocialLikesRepository.fetch_one(query, (user_id, post_id))

    @staticmethod
    def delete_like(user_id: str, post_id: str) -> bool:
        """
        Unlike a post.

        Returns:
            True if deleted, False otherwise
        """
        query = """
            DELETE FROM social.social_likes
            WHERE user_id = %s AND post_id = %s
        """
        result = SocialLikesRepository.execute(query, (user_id, post_id))
        return result > 0

    @staticmethod
    def get_like(user_id: str, post_id: str) -> Optional[Dict[str, Any]]:
        """Check if user has liked a post."""
        query = """
            SELECT * FROM social.social_likes
            WHERE user_id = %s AND post_id = %s
        """
        return SocialLikesRepository.fetch_one(query, (user_id, post_id))

    @staticmethod
    def get_post_likes(post_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all users who liked a post."""
        query = """
            SELECT l.*, u.email, u.username, u.profile_picture_url
            FROM social.social_likes l
            JOIN users u ON l.user_id = u.user_id
            WHERE l.post_id = %s
            ORDER BY l.created_at DESC
            LIMIT %s OFFSET %s
        """
        return SocialLikesRepository.fetch_all(query, (post_id, limit, offset))

    # =====================
    # REACTIONS (Extended Likes)
    # =====================

    @staticmethod
    def create_reaction(user_id: str, post_id: str, reaction_type: str) -> Optional[Dict[str, Any]]:
        """
        Add a reaction to a post.

        Args:
            user_id: User ID
            post_id: Post ID
            reaction_type: like, love, haha, wow, sad, angry, thinking, celebrate

        Returns:
            Created reaction record
        """
        query = """
            INSERT INTO social.social_reactions (user_id, post_id, reaction_type)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, post_id)
            DO UPDATE SET reaction_type = EXCLUDED.reaction_type, created_at = CURRENT_TIMESTAMP
            RETURNING *
        """
        return SocialLikesRepository.fetch_one(query, (user_id, post_id, reaction_type))

    @staticmethod
    def delete_reaction(user_id: str, post_id: str) -> bool:
        """Remove reaction from a post."""
        query = """
            DELETE FROM social.social_reactions
            WHERE user_id = %s AND post_id = %s
        """
        result = SocialLikesRepository.execute(query, (user_id, post_id))
        return result > 0

    @staticmethod
    def get_reaction(user_id: str, post_id: str) -> Optional[Dict[str, Any]]:
        """Get user's reaction on a post."""
        query = """
            SELECT * FROM social.social_reactions
            WHERE user_id = %s AND post_id = %s
        """
        return SocialLikesRepository.fetch_one(query, (user_id, post_id))

    @staticmethod
    def get_post_reactions(post_id: str) -> List[Dict[str, Any]]:
        """Get all reactions for a post with counts."""
        query = """
            SELECT reaction_type, COUNT(*) as count
            FROM social.social_reactions
            WHERE post_id = %s
            GROUP BY reaction_type
            ORDER BY count DESC
        """
        return SocialLikesRepository.fetch_all(query, (post_id,))

    # =====================
    # SHARES
    # =====================

    @staticmethod
    def create_share(user_id: str, post_id: str,
                    share_caption: Optional[str] = None,
                    share_type: str = 'repost') -> Optional[Dict[str, Any]]:
        """
        Share a post.

        Args:
            user_id: User ID who shares
            post_id: Post ID being shared
            share_caption: Optional caption for the share
            share_type: repost, quote, external

        Returns:
            Created share record
        """
        query = """
            INSERT INTO social.social_shares
            (user_id, post_id, share_type, share_caption)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """
        return SocialLikesRepository.fetch_one(
            query, (user_id, post_id, share_type, share_caption)
        )

    @staticmethod
    def delete_share(share_id: str, user_id: str) -> bool:
        """Delete a share (only if owned by user)."""
        query = """
            DELETE FROM social.social_shares
            WHERE share_id = %s AND user_id = %s
        """
        result = SocialLikesRepository.execute(query, (share_id, user_id))
        return result > 0

    @staticmethod
    def get_post_shares(post_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all shares of a post."""
        query = """
            SELECT s.*, u.email, u.username, u.profile_picture_url
            FROM social.social_shares s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.post_id = %s
            ORDER BY s.created_at DESC
            LIMIT %s OFFSET %s
        """
        return SocialLikesRepository.fetch_all(query, (post_id, limit, offset))

    @staticmethod
    def get_user_shares(user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all posts shared by a user."""
        query = """
            SELECT s.*, p.*
            FROM social.social_shares s
            JOIN social.social_posts p ON s.post_id = p.post_id
            WHERE s.user_id = %s
            ORDER BY s.created_at DESC
            LIMIT %s OFFSET %s
        """
        return SocialLikesRepository.fetch_all(query, (user_id, limit, offset))

    # =====================
    # BOOKMARKS
    # =====================

    @staticmethod
    def create_bookmark(user_id: str, post_id: str,
                       collection_id: Optional[str] = None,
                       notes: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Bookmark a post.

        Args:
            user_id: User ID
            post_id: Post ID
            collection_id: Optional collection to add to
            notes: Optional private notes

        Returns:
            Created bookmark record
        """
        query = """
            INSERT INTO social.social_bookmarks
            (user_id, post_id, collection_id, notes)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id, post_id) DO NOTHING
            RETURNING *
        """
        return SocialLikesRepository.fetch_one(
            query, (user_id, post_id, collection_id, notes)
        )

    @staticmethod
    def delete_bookmark(user_id: str, post_id: str) -> bool:
        """Remove a bookmark."""
        query = """
            DELETE FROM social.social_bookmarks
            WHERE user_id = %s AND post_id = %s
        """
        result = SocialLikesRepository.execute(query, (user_id, post_id))
        return result > 0

    @staticmethod
    def get_bookmark(user_id: str, post_id: str) -> Optional[Dict[str, Any]]:
        """Check if user has bookmarked a post."""
        query = """
            SELECT * FROM social.social_bookmarks
            WHERE user_id = %s AND post_id = %s
        """
        return SocialLikesRepository.fetch_one(query, (user_id, post_id))

    @staticmethod
    def get_user_bookmarks(user_id: str, collection_id: Optional[str] = None,
                          limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all bookmarks for a user (optionally filtered by collection)."""
        if collection_id:
            query = """
                SELECT b.*, p.*
                FROM social.social_bookmarks b
                JOIN social.social_posts p ON b.post_id = p.post_id
                WHERE b.user_id = %s AND b.collection_id = %s
                ORDER BY b.created_at DESC
                LIMIT %s OFFSET %s
            """
            return SocialLikesRepository.fetch_all(
                query, (user_id, collection_id, limit, offset)
            )
        else:
            query = """
                SELECT b.*, p.*
                FROM social.social_bookmarks b
                JOIN social.social_posts p ON b.post_id = p.post_id
                WHERE b.user_id = %s
                ORDER BY b.created_at DESC
                LIMIT %s OFFSET %s
            """
            return SocialLikesRepository.fetch_all(query, (user_id, limit, offset))

    @staticmethod
    def update_bookmark_notes(user_id: str, post_id: str, notes: str) -> Optional[Dict[str, Any]]:
        """Update private notes on a bookmark."""
        query = """
            UPDATE social.social_bookmarks
            SET notes = %s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s AND post_id = %s
            RETURNING *
        """
        return SocialLikesRepository.fetch_one(query, (notes, user_id, post_id))

    # =====================
    # BOOKMARK COLLECTIONS
    # =====================

    @staticmethod
    def create_collection(user_id: str, name: str,
                         description: Optional[str] = None,
                         is_private: bool = True) -> Optional[Dict[str, Any]]:
        """Create a bookmark collection."""
        query = """
            INSERT INTO social.social_bookmark_collections
            (user_id, name, description, is_private)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """
        return SocialLikesRepository.fetch_one(
            query, (user_id, name, description, is_private)
        )

    @staticmethod
    def get_user_collections(user_id: str) -> List[Dict[str, Any]]:
        """Get all bookmark collections for a user."""
        query = """
            SELECT * FROM social.social_bookmark_collections
            WHERE user_id = %s
            ORDER BY created_at DESC
        """
        return SocialLikesRepository.fetch_all(query, (user_id,))

    @staticmethod
    def update_collection(collection_id: str, user_id: str,
                         name: Optional[str] = None,
                         description: Optional[str] = None,
                         is_private: Optional[bool] = None) -> Optional[Dict[str, Any]]:
        """Update a bookmark collection."""
        updates = []
        params = []

        if name is not None:
            updates.append("name = %s")
            params.append(name)
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        if is_private is not None:
            updates.append("is_private = %s")
            params.append(is_private)

        if not updates:
            return None

        params.extend([collection_id, user_id])
        query = f"""
            UPDATE social.social_bookmark_collections
            SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
            WHERE collection_id = %s AND user_id = %s
            RETURNING *
        """
        return SocialLikesRepository.fetch_one(query, tuple(params))

    @staticmethod
    def delete_collection(collection_id: str, user_id: str) -> bool:
        """Delete a bookmark collection (sets bookmarks' collection_id to NULL via trigger)."""
        query = """
            DELETE FROM social.social_bookmark_collections
            WHERE collection_id = %s AND user_id = %s
        """
        result = SocialLikesRepository.execute(query, (collection_id, user_id))
        return result > 0
