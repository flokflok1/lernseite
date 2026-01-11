"""
Social Comments Repository

Handles database operations for comments, threaded replies, and comment likes.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from app.repositories.base_repository import BaseRepository


class SocialCommentsRepository(BaseRepository):
    """Repository for social_comments and related tables"""

    # =====================
    # COMMENTS
    # =====================

    @staticmethod
    def create_comment(user_id: str, post_id: str, content: str,
                      parent_comment_id: Optional[str] = None,
                      thread_level: int = 0) -> Optional[Dict[str, Any]]:
        """
        Create a comment on a post.

        Args:
            user_id: User ID who comments
            post_id: Post ID being commented on
            content: Comment text (max 2000 chars)
            parent_comment_id: Parent comment for threading (max depth 2)
            thread_level: 0 (root), 1 (reply), 2 (reply to reply)

        Returns:
            Created comment record
        """
        query = """
            INSERT INTO social.social_comments
            (user_id, post_id, content, parent_comment_id, thread_level)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        """
        return SocialCommentsRepository.fetch_one(
            query, (user_id, post_id, content, parent_comment_id, thread_level)
        )

    @staticmethod
    def get_comment(comment_id: str) -> Optional[Dict[str, Any]]:
        """Get a single comment by ID."""
        query = """
            SELECT c.*, u.email, u.username, u.profile_picture_url
            FROM social.social_comments c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.comment_id = %s AND c.is_deleted = FALSE
        """
        return SocialCommentsRepository.fetch_one(query, (comment_id,))

    @staticmethod
    def update_comment(comment_id: str, user_id: str, content: str) -> Optional[Dict[str, Any]]:
        """
        Update comment content (only if owned by user).

        Args:
            comment_id: Comment ID
            user_id: User ID (must match comment owner)
            content: New content

        Returns:
            Updated comment or None
        """
        query = """
            UPDATE social.social_comments
            SET content = %s, is_edited = TRUE, updated_at = CURRENT_TIMESTAMP
            WHERE comment_id = %s AND user_id = %s AND is_deleted = FALSE
            RETURNING *
        """
        return SocialCommentsRepository.fetch_one(query, (content, comment_id, user_id))

    @staticmethod
    def soft_delete_comment(comment_id: str, user_id: str) -> bool:
        """
        Soft delete a comment (only if owned by user).

        Returns:
            True if deleted, False otherwise
        """
        query = """
            UPDATE social.social_comments
            SET is_deleted = TRUE, deleted_at = CURRENT_TIMESTAMP
            WHERE comment_id = %s AND user_id = %s
        """
        result = SocialCommentsRepository.execute(query, (comment_id, user_id))
        return result > 0

    @staticmethod
    def get_post_comments(post_id: str, limit: int = 50, offset: int = 0,
                         sort: str = 'recent') -> List[Dict[str, Any]]:
        """
        Get root-level comments for a post.

        Args:
            post_id: Post ID
            limit: Max comments to return
            offset: Pagination offset
            sort: 'recent', 'popular', 'oldest'

        Returns:
            List of root comments (thread_level = 0)
        """
        order_by = {
            'recent': 'c.created_at DESC',
            'popular': 'c.likes_count DESC, c.created_at DESC',
            'oldest': 'c.created_at ASC'
        }.get(sort, 'c.created_at DESC')

        query = f"""
            SELECT c.*, u.email, u.username, u.profile_picture_url
            FROM social.social_comments c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.post_id = %s AND c.thread_level = 0 AND c.is_deleted = FALSE
            ORDER BY {order_by}
            LIMIT %s OFFSET %s
        """
        return SocialCommentsRepository.fetch_all(query, (post_id, limit, offset))

    @staticmethod
    def get_comment_replies(parent_comment_id: str, limit: int = 20,
                           offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get replies to a comment (thread_level 1 and 2).

        Args:
            parent_comment_id: Parent comment ID
            limit: Max replies
            offset: Pagination offset

        Returns:
            List of replies
        """
        query = """
            SELECT c.*, u.email, u.username, u.profile_picture_url
            FROM social.social_comments c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.parent_comment_id = %s AND c.is_deleted = FALSE
            ORDER BY c.created_at ASC
            LIMIT %s OFFSET %s
        """
        return SocialCommentsRepository.fetch_all(query, (parent_comment_id, limit, offset))

    @staticmethod
    def get_user_comments(user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all comments by a user."""
        query = """
            SELECT c.*, p.post_id, p.content as post_content
            FROM social.social_comments c
            JOIN social.social_posts p ON c.post_id = p.post_id
            WHERE c.user_id = %s AND c.is_deleted = FALSE
            ORDER BY c.created_at DESC
            LIMIT %s OFFSET %s
        """
        return SocialCommentsRepository.fetch_all(query, (user_id, limit, offset))

    @staticmethod
    def get_comment_count(post_id: str) -> int:
        """Get total comment count for a post (including replies)."""
        query = """
            SELECT COUNT(*) as count
            FROM social.social_comments
            WHERE post_id = %s AND is_deleted = FALSE
        """
        result = SocialCommentsRepository.fetch_one(query, (post_id,))
        return result['count'] if result else 0

    # =====================
    # COMMENT LIKES
    # =====================

    @staticmethod
    def like_comment(user_id: str, comment_id: str) -> Optional[Dict[str, Any]]:
        """
        Like a comment.

        Args:
            user_id: User ID
            comment_id: Comment ID

        Returns:
            Created like record
        """
        query = """
            INSERT INTO social.social_comment_likes (user_id, comment_id)
            VALUES (%s, %s)
            ON CONFLICT (user_id, comment_id) DO NOTHING
            RETURNING *
        """
        return SocialCommentsRepository.fetch_one(query, (user_id, comment_id))

    @staticmethod
    def unlike_comment(user_id: str, comment_id: str) -> bool:
        """
        Unlike a comment.

        Returns:
            True if deleted, False otherwise
        """
        query = """
            DELETE FROM social.social_comment_likes
            WHERE user_id = %s AND comment_id = %s
        """
        result = SocialCommentsRepository.execute(query, (user_id, comment_id))
        return result > 0

    @staticmethod
    def get_comment_like(user_id: str, comment_id: str) -> Optional[Dict[str, Any]]:
        """Check if user has liked a comment."""
        query = """
            SELECT * FROM social.social_comment_likes
            WHERE user_id = %s AND comment_id = %s
        """
        return SocialCommentsRepository.fetch_one(query, (user_id, comment_id))

    @staticmethod
    def get_comment_likes(comment_id: str, limit: int = 50,
                         offset: int = 0) -> List[Dict[str, Any]]:
        """Get all users who liked a comment."""
        query = """
            SELECT l.*, u.email, u.username, u.profile_picture_url
            FROM social.social_comment_likes l
            JOIN users u ON l.user_id = u.user_id
            WHERE l.comment_id = %s
            ORDER BY l.created_at DESC
            LIMIT %s OFFSET %s
        """
        return SocialCommentsRepository.fetch_all(query, (comment_id, limit, offset))

    # =====================
    # THREAD MANAGEMENT
    # =====================

    @staticmethod
    def get_thread_depth(comment_id: str) -> int:
        """Get current thread depth of a comment."""
        query = """
            SELECT thread_level FROM social.social_comments
            WHERE comment_id = %s
        """
        result = SocialCommentsRepository.fetch_one(query, (comment_id,))
        return result['thread_level'] if result else 0

    @staticmethod
    def get_comment_tree(post_id: str, max_depth: int = 2) -> List[Dict[str, Any]]:
        """
        Get complete comment tree for a post (hierarchical).

        Args:
            post_id: Post ID
            max_depth: Max thread depth (0-2)

        Returns:
            List of comments with nested replies
        """
        # Get all comments
        query = """
            SELECT c.*, u.email, u.username, u.profile_picture_url
            FROM social.social_comments c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.post_id = %s AND c.thread_level <= %s AND c.is_deleted = FALSE
            ORDER BY c.thread_level ASC, c.created_at ASC
        """
        comments = SocialCommentsRepository.fetch_all(query, (post_id, max_depth))

        # Build tree structure
        comment_map = {}
        root_comments = []

        for comment in comments:
            comment['replies'] = []
            comment_map[comment['comment_id']] = comment

            if comment['parent_comment_id'] is None:
                root_comments.append(comment)
            else:
                parent = comment_map.get(comment['parent_comment_id'])
                if parent:
                    parent['replies'].append(comment)

        return root_comments

    @staticmethod
    def pin_comment(comment_id: str, post_author_id: str) -> Optional[Dict[str, Any]]:
        """
        Pin a comment (only post author can pin).

        Args:
            comment_id: Comment ID
            post_author_id: Post author user ID (for authorization)

        Returns:
            Updated comment or None
        """
        query = """
            UPDATE social.social_comments c
            SET is_pinned = TRUE, updated_at = CURRENT_TIMESTAMP
            WHERE c.comment_id = %s
            AND c.post_id IN (
                SELECT post_id FROM social.social_posts
                WHERE user_id = %s
            )
            RETURNING *
        """
        return SocialCommentsRepository.fetch_one(query, (comment_id, post_author_id))

    @staticmethod
    def unpin_comment(comment_id: str, post_author_id: str) -> Optional[Dict[str, Any]]:
        """Unpin a comment (only post author can unpin)."""
        query = """
            UPDATE social.social_comments c
            SET is_pinned = FALSE, updated_at = CURRENT_TIMESTAMP
            WHERE c.comment_id = %s
            AND c.post_id IN (
                SELECT post_id FROM social.social_posts
                WHERE user_id = %s
            )
            RETURNING *
        """
        return SocialCommentsRepository.fetch_one(query, (comment_id, post_author_id))

    @staticmethod
    def get_pinned_comments(post_id: str) -> List[Dict[str, Any]]:
        """Get all pinned comments for a post."""
        query = """
            SELECT c.*, u.email, u.username, u.profile_picture_url
            FROM social.social_comments c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.post_id = %s AND c.is_pinned = TRUE AND c.is_deleted = FALSE
            ORDER BY c.created_at DESC
        """
        return SocialCommentsRepository.fetch_all(query, (post_id,))
