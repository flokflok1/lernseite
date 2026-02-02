"""
Comments Service

Manages comments, threaded replies, and comment likes.
Max thread depth: 2 (comment → reply → reply to reply).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from app.infrastructure.persistence.repositories.social_comments import SocialCommentsRepository
from app.infrastructure.persistence.repositories.social_posts import SocialPostsRepository


class CommentsService:
    """Service for managing comments and replies"""

    MAX_THREAD_DEPTH = 2  # comment → reply → reply to reply

    # =====================
    # COMMENTS
    # =====================

    @staticmethod
    def create_comment(user_id: str, post_id: str, content: str,
                      parent_comment_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a comment on a post.

        Args:
            user_id: User ID
            post_id: Post ID
            content: Comment text (max 2000 chars)
            parent_comment_id: Optional parent for threading

        Returns:
            Success status and comment record
        """
        # Validate content length
        if not content or len(content) > 2000:
            return {
                'success': False,
                'error': 'Comment must be between 1 and 2000 characters'
            }

        # Check if post exists
        post = SocialPostsRepository.get_by_id(post_id)
        if not post:
            return {
                'success': False,
                'error': 'Post not found'
            }

        # Determine thread level
        thread_level = 0
        if parent_comment_id:
            parent = SocialCommentsRepository.get_comment(parent_comment_id)
            if not parent:
                return {
                    'success': False,
                    'error': 'Parent comment not found'
                }

            thread_level = parent['thread_level'] + 1

            # Enforce max depth
            if thread_level > CommentsService.MAX_THREAD_DEPTH:
                return {
                    'success': False,
                    'error': f'Maximum thread depth ({CommentsService.MAX_THREAD_DEPTH}) exceeded'
                }

        # Create comment (trigger updates comments_count)
        comment = SocialCommentsRepository.create_comment(
            user_id, post_id, content, parent_comment_id, thread_level
        )

        if comment:
            return {
                'success': True,
                'data': comment
            }
        else:
            return {
                'success': False,
                'error': 'Failed to create comment'
            }

    @staticmethod
    def update_comment(comment_id: str, user_id: str, content: str) -> Dict[str, Any]:
        """
        Update comment content (only if owned by user).

        Args:
            comment_id: Comment ID
            user_id: User ID (must match owner)
            content: New content

        Returns:
            Success status and updated comment
        """
        if not content or len(content) > 2000:
            return {
                'success': False,
                'error': 'Comment must be between 1 and 2000 characters'
            }

        comment = SocialCommentsRepository.update_comment(comment_id, user_id, content)

        if comment:
            return {
                'success': True,
                'data': comment
            }
        else:
            return {
                'success': False,
                'error': 'Comment not found or not owned by you'
            }

    @staticmethod
    def delete_comment(comment_id: str, user_id: str) -> Dict[str, Any]:
        """
        Soft delete a comment (only if owned by user).

        Returns:
            Success status
        """
        success = SocialCommentsRepository.soft_delete_comment(comment_id, user_id)

        if success:
            return {
                'success': True,
                'message': 'Comment deleted'
            }
        else:
            return {
                'success': False,
                'error': 'Comment not found or not owned by you'
            }

    @staticmethod
    def get_comment(comment_id: str) -> Optional[Dict[str, Any]]:
        """Get a single comment by ID."""
        return SocialCommentsRepository.get_comment(comment_id)

    @staticmethod
    def get_post_comments(post_id: str, limit: int = 50, offset: int = 0,
                         sort: str = 'recent') -> Dict[str, Any]:
        """
        Get root-level comments for a post.

        Args:
            post_id: Post ID
            limit: Max comments
            offset: Pagination offset
            sort: 'recent', 'popular', 'oldest'

        Returns:
            Comments list and metadata
        """
        valid_sorts = ['recent', 'popular', 'oldest']
        if sort not in valid_sorts:
            sort = 'recent'

        comments = SocialCommentsRepository.get_post_comments(post_id, limit, offset, sort)

        # Get total count
        total = SocialCommentsRepository.get_comment_count(post_id)

        return {
            'comments': comments,
            'meta': {
                'total': total,
                'limit': limit,
                'offset': offset,
                'sort': sort
            }
        }

    @staticmethod
    def get_comment_replies(parent_comment_id: str, limit: int = 20,
                           offset: int = 0) -> List[Dict[str, Any]]:
        """Get replies to a comment."""
        return SocialCommentsRepository.get_comment_replies(
            parent_comment_id, limit, offset
        )

    @staticmethod
    def get_user_comments(user_id: str, limit: int = 50,
                         offset: int = 0) -> List[Dict[str, Any]]:
        """Get all comments by a user."""
        return SocialCommentsRepository.get_user_comments(user_id, limit, offset)

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
        if max_depth > CommentsService.MAX_THREAD_DEPTH:
            max_depth = CommentsService.MAX_THREAD_DEPTH

        return SocialCommentsRepository.get_comment_tree(post_id, max_depth)

    # =====================
    # COMMENT LIKES
    # =====================

    @staticmethod
    def like_comment(user_id: str, comment_id: str) -> Dict[str, Any]:
        """
        Like a comment.

        Args:
            user_id: User ID
            comment_id: Comment ID

        Returns:
            Success status and like record
        """
        # Check if comment exists
        comment = SocialCommentsRepository.get_comment(comment_id)
        if not comment:
            return {
                'success': False,
                'error': 'Comment not found'
            }

        # Check if already liked
        existing = SocialCommentsRepository.get_comment_like(user_id, comment_id)
        if existing:
            return {
                'success': False,
                'error': 'Already liked',
                'data': existing
            }

        # Create like (trigger updates likes_count)
        like = SocialCommentsRepository.like_comment(user_id, comment_id)

        if like:
            return {
                'success': True,
                'data': like
            }
        else:
            return {
                'success': False,
                'error': 'Failed to like comment'
            }

    @staticmethod
    def unlike_comment(user_id: str, comment_id: str) -> Dict[str, Any]:
        """Unlike a comment."""
        success = SocialCommentsRepository.unlike_comment(user_id, comment_id)

        if success:
            return {
                'success': True,
                'message': 'Comment unliked'
            }
        else:
            return {
                'success': False,
                'error': 'Not liked'
            }

    @staticmethod
    def get_comment_likes(comment_id: str, limit: int = 50,
                         offset: int = 0) -> List[Dict[str, Any]]:
        """Get all users who liked a comment."""
        return SocialCommentsRepository.get_comment_likes(comment_id, limit, offset)

    # =====================
    # MODERATION (Post Author)
    # =====================

    @staticmethod
    def pin_comment(comment_id: str, post_author_id: str) -> Dict[str, Any]:
        """
        Pin a comment (only post author can pin).

        Args:
            comment_id: Comment ID
            post_author_id: Post author user ID

        Returns:
            Success status and pinned comment
        """
        comment = SocialCommentsRepository.pin_comment(comment_id, post_author_id)

        if comment:
            return {
                'success': True,
                'data': comment
            }
        else:
            return {
                'success': False,
                'error': 'Comment not found or you are not the post author'
            }

    @staticmethod
    def unpin_comment(comment_id: str, post_author_id: str) -> Dict[str, Any]:
        """Unpin a comment (only post author can unpin)."""
        comment = SocialCommentsRepository.unpin_comment(comment_id, post_author_id)

        if comment:
            return {
                'success': True,
                'data': comment
            }
        else:
            return {
                'success': False,
                'error': 'Comment not found or you are not the post author'
            }

    @staticmethod
    def get_pinned_comments(post_id: str) -> List[Dict[str, Any]]:
        """Get all pinned comments for a post."""
        return SocialCommentsRepository.get_pinned_comments(post_id)
