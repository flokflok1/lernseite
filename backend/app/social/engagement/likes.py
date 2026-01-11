"""
Likes & Reactions Service

Manages likes, reactions, shares, and bookmarks.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from app.repositories.social_likes import SocialLikesRepository
from app.repositories.social_posts import SocialPostsRepository


class LikesService:
    """Service for managing likes and reactions"""

    # =====================
    # LIKES
    # =====================

    @staticmethod
    def like_post(user_id: str, post_id: str) -> Dict[str, Any]:
        """
        Like a post.

        Args:
            user_id: User ID
            post_id: Post ID

        Returns:
            Success status and like record
        """
        # Check if post exists
        post = SocialPostsRepository.get_by_id(post_id)
        if not post:
            return {
                'success': False,
                'error': 'Post not found'
            }

        # Check if already liked
        existing = SocialLikesRepository.get_like(user_id, post_id)
        if existing:
            return {
                'success': False,
                'error': 'Already liked',
                'data': existing
            }

        # Create like (trigger updates likes_count)
        like = SocialLikesRepository.create_like(user_id, post_id)

        if like:
            return {
                'success': True,
                'data': like
            }
        else:
            return {
                'success': False,
                'error': 'Failed to like post'
            }

    @staticmethod
    def unlike_post(user_id: str, post_id: str) -> Dict[str, Any]:
        """Unlike a post."""
        success = SocialLikesRepository.delete_like(user_id, post_id)

        if success:
            return {
                'success': True,
                'message': 'Unliked successfully'
            }
        else:
            return {
                'success': False,
                'error': 'Not liked'
            }

    @staticmethod
    def get_post_likes(post_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all users who liked a post."""
        return SocialLikesRepository.get_post_likes(post_id, limit, offset)

    # =====================
    # REACTIONS (Extended Likes)
    # =====================

    @staticmethod
    def add_reaction(user_id: str, post_id: str, reaction_type: str) -> Dict[str, Any]:
        """
        Add a reaction to a post.

        Args:
            user_id: User ID
            post_id: Post ID
            reaction_type: like, love, haha, wow, sad, angry, thinking, celebrate

        Returns:
            Success status and reaction record
        """
        valid_reactions = ['like', 'love', 'haha', 'wow', 'sad', 'angry', 'thinking', 'celebrate']

        if reaction_type not in valid_reactions:
            return {
                'success': False,
                'error': f'Invalid reaction type. Must be one of: {", ".join(valid_reactions)}'
            }

        # Check if post exists
        post = SocialPostsRepository.get_by_id(post_id)
        if not post:
            return {
                'success': False,
                'error': 'Post not found'
            }

        # Create or update reaction
        reaction = SocialLikesRepository.create_reaction(user_id, post_id, reaction_type)

        if reaction:
            return {
                'success': True,
                'data': reaction
            }
        else:
            return {
                'success': False,
                'error': 'Failed to add reaction'
            }

    @staticmethod
    def remove_reaction(user_id: str, post_id: str) -> Dict[str, Any]:
        """Remove reaction from a post."""
        success = SocialLikesRepository.delete_reaction(user_id, post_id)

        if success:
            return {
                'success': True,
                'message': 'Reaction removed'
            }
        else:
            return {
                'success': False,
                'error': 'No reaction found'
            }

    @staticmethod
    def get_post_reactions(post_id: str) -> Dict[str, Any]:
        """
        Get reaction summary for a post.

        Returns:
            Dict with reaction counts
        """
        reactions = SocialLikesRepository.get_post_reactions(post_id)

        # Convert to dict
        reaction_summary = {
            'like': 0, 'love': 0, 'haha': 0, 'wow': 0,
            'sad': 0, 'angry': 0, 'thinking': 0, 'celebrate': 0
        }

        total = 0
        for reaction in reactions:
            reaction_summary[reaction['reaction_type']] = reaction['count']
            total += reaction['count']

        return {
            'reactions': reaction_summary,
            'total': total
        }

    # =====================
    # SHARES
    # =====================

    @staticmethod
    def share_post(user_id: str, post_id: str,
                  share_caption: Optional[str] = None,
                  share_type: str = 'repost') -> Dict[str, Any]:
        """
        Share a post.

        Args:
            user_id: User ID
            post_id: Post ID
            share_caption: Optional caption
            share_type: repost, quote, external

        Returns:
            Success status and share record
        """
        valid_share_types = ['repost', 'quote', 'external']

        if share_type not in valid_share_types:
            return {
                'success': False,
                'error': f'Invalid share type. Must be one of: {", ".join(valid_share_types)}'
            }

        # Check if post exists
        post = SocialPostsRepository.get_by_id(post_id)
        if not post:
            return {
                'success': False,
                'error': 'Post not found'
            }

        # Create share (trigger updates shares_count)
        share = SocialLikesRepository.create_share(
            user_id, post_id, share_caption, share_type
        )

        if share:
            return {
                'success': True,
                'data': share
            }
        else:
            return {
                'success': False,
                'error': 'Failed to share post'
            }

    @staticmethod
    def delete_share(share_id: str, user_id: str) -> Dict[str, Any]:
        """Delete a share (only if owned by user)."""
        success = SocialLikesRepository.delete_share(share_id, user_id)

        if success:
            return {
                'success': True,
                'message': 'Share deleted'
            }
        else:
            return {
                'success': False,
                'error': 'Share not found or not owned by you'
            }

    @staticmethod
    def get_post_shares(post_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all shares of a post."""
        return SocialLikesRepository.get_post_shares(post_id, limit, offset)

    @staticmethod
    def get_user_shares(user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all posts shared by a user."""
        return SocialLikesRepository.get_user_shares(user_id, limit, offset)

    # =====================
    # BOOKMARKS
    # =====================

    @staticmethod
    def bookmark_post(user_id: str, post_id: str,
                     collection_id: Optional[str] = None,
                     notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Bookmark a post.

        Args:
            user_id: User ID
            post_id: Post ID
            collection_id: Optional collection
            notes: Optional private notes

        Returns:
            Success status and bookmark record
        """
        # Check if post exists
        post = SocialPostsRepository.get_by_id(post_id)
        if not post:
            return {
                'success': False,
                'error': 'Post not found'
            }

        # Check if already bookmarked
        existing = SocialLikesRepository.get_bookmark(user_id, post_id)
        if existing:
            return {
                'success': False,
                'error': 'Already bookmarked',
                'data': existing
            }

        # Create bookmark
        bookmark = SocialLikesRepository.create_bookmark(
            user_id, post_id, collection_id, notes
        )

        if bookmark:
            return {
                'success': True,
                'data': bookmark
            }
        else:
            return {
                'success': False,
                'error': 'Failed to bookmark post'
            }

    @staticmethod
    def remove_bookmark(user_id: str, post_id: str) -> Dict[str, Any]:
        """Remove a bookmark."""
        success = SocialLikesRepository.delete_bookmark(user_id, post_id)

        if success:
            return {
                'success': True,
                'message': 'Bookmark removed'
            }
        else:
            return {
                'success': False,
                'error': 'Not bookmarked'
            }

    @staticmethod
    def get_bookmarks(user_id: str, collection_id: Optional[str] = None,
                     limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all bookmarks for a user (optionally filtered by collection)."""
        return SocialLikesRepository.get_user_bookmarks(
            user_id, collection_id, limit, offset
        )

    @staticmethod
    def update_bookmark_notes(user_id: str, post_id: str, notes: str) -> Dict[str, Any]:
        """Update private notes on a bookmark."""
        bookmark = SocialLikesRepository.update_bookmark_notes(user_id, post_id, notes)

        if bookmark:
            return {
                'success': True,
                'data': bookmark
            }
        else:
            return {
                'success': False,
                'error': 'Bookmark not found'
            }

    # =====================
    # BOOKMARK COLLECTIONS
    # =====================

    @staticmethod
    def create_collection(user_id: str, name: str,
                         description: Optional[str] = None,
                         is_private: bool = True) -> Dict[str, Any]:
        """Create a bookmark collection."""
        collection = SocialLikesRepository.create_collection(
            user_id, name, description, is_private
        )

        if collection:
            return {
                'success': True,
                'data': collection
            }
        else:
            return {
                'success': False,
                'error': 'Failed to create collection'
            }

    @staticmethod
    def get_collections(user_id: str) -> List[Dict[str, Any]]:
        """Get all bookmark collections for a user."""
        return SocialLikesRepository.get_user_collections(user_id)

    @staticmethod
    def update_collection(collection_id: str, user_id: str,
                         name: Optional[str] = None,
                         description: Optional[str] = None,
                         is_private: Optional[bool] = None) -> Dict[str, Any]:
        """Update a bookmark collection."""
        collection = SocialLikesRepository.update_collection(
            collection_id, user_id, name, description, is_private
        )

        if collection:
            return {
                'success': True,
                'data': collection
            }
        else:
            return {
                'success': False,
                'error': 'Collection not found or no changes made'
            }

    @staticmethod
    def delete_collection(collection_id: str, user_id: str) -> Dict[str, Any]:
        """Delete a bookmark collection."""
        success = SocialLikesRepository.delete_collection(collection_id, user_id)

        if success:
            return {
                'success': True,
                'message': 'Collection deleted (bookmarks moved to default)'
            }
        else:
            return {
                'success': False,
                'error': 'Collection not found'
            }
