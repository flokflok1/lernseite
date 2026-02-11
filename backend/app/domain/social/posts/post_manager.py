"""
Post Manager - Post CRUD Operations

Handles all post creation, reading, updating, and deletion logic.
"""

from typing import Optional, Dict, List
from datetime import datetime
from app.domain.ports.core.registry import repos


class PostManager:
    """
    Manages social posts (create, read, update, delete)
    """

    @staticmethod
    def create_post(
        user_id: str,
        content: Optional[str],
        content_type: str = 'text',
        visibility: str = 'public',
        media_urls: List[str] = None,
        mentions: List[str] = None,
        hashtags: List[str] = None
    ) -> Dict:
        """
        Create a new post

        Args:
            user_id: Creator user ID
            content: Post text content
            content_type: 'text', 'media', 'course_portfolio', 'achievement'
            visibility: 'public', 'followers', 'private', 'unlisted'
            media_urls: Optional list of media URLs
            mentions: Optional list of user IDs to mention
            hashtags: Optional list of hashtags (without #)

        Returns:
            Dict with post data
        """
        from app.domain.social.posts.media_handler import MediaHandler
        from app.domain.ai.content_moderation.text_classifier import TextClassifier

        # AI Moderation (ALWAYS ENABLED - child_safety_strict flag)
        moderation_result = TextClassifier.moderate_content(content or '')
        moderation_status = 'pending' if moderation_result['flagged'] else 'ai_approved'

        # Create post
        post_data = {
            'user_id': user_id,
            'content': content,
            'content_type': content_type,
            'visibility': visibility,
            'moderation_status': moderation_status,
            'created_at': datetime.utcnow()
        }

        post = repos.social_posts.create(post_data)

        # Handle media attachments
        if media_urls:
            MediaHandler.attach_media(post['post_id'], media_urls)

        # Handle mentions
        if mentions:
            PostManager._handle_mentions(post['post_id'], mentions)

        # Handle hashtags
        if hashtags:
            PostManager._handle_hashtags(post['post_id'], hashtags)

        return post

    @staticmethod
    def get_post(post_id: str, viewer_user_id: str) -> Optional[Dict]:
        """
        Get post by ID (with privacy checks)

        Args:
            post_id: Post ID
            viewer_user_id: User viewing the post

        Returns:
            Post data or None if not found/no access
        """
        post = repos.social_posts.get_by_id(post_id)

        if not post:
            return None

        # Privacy check
        if post['visibility'] == 'private' and post['user_id'] != viewer_user_id:
            return None

        if post['visibility'] == 'followers':
            if not repos.social_follows.is_following(viewer_user_id, post['user_id']):
                return None

        return post

    @staticmethod
    def update_post(
        post_id: str,
        user_id: str,
        content: Optional[str] = None,
        visibility: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Update post (must be owner)

        Args:
            post_id: Post ID
            user_id: User ID (must be post owner)
            content: Updated content
            visibility: Updated visibility

        Returns:
            Updated post or None if not found/no permission
        """
        post = repos.social_posts.get_by_id(post_id)

        if not post or post['user_id'] != user_id:
            return None

        update_data = {}
        if content is not None:
            update_data['content'] = content
            update_data['is_edited'] = True
            update_data['edited_at'] = datetime.utcnow()

        if visibility is not None:
            update_data['visibility'] = visibility

        if update_data:
            return repos.social_posts.update(post_id, update_data)

        return post

    @staticmethod
    def delete_post(post_id: str, user_id: str) -> bool:
        """
        Delete post (soft delete, must be owner)

        Args:
            post_id: Post ID
            user_id: User ID (must be post owner)

        Returns:
            True if deleted, False if not found/no permission
        """
        post = repos.social_posts.get_by_id(post_id)

        if not post or post['user_id'] != user_id:
            return False

        return repos.social_posts.soft_delete(post_id)

    @staticmethod
    def get_user_posts(
        target_user_id: str,
        viewer_user_id: str,
        page: int = 1,
        per_page: int = 20
    ) -> Dict:
        """
        Get user's posts (with privacy filtering)

        Args:
            target_user_id: User whose posts to get
            viewer_user_id: User viewing the posts
            page: Page number
            per_page: Posts per page

        Returns:
            Dict with posts list and pagination info
        """
        posts = repos.social_posts.get_user_posts(
            user_id=target_user_id,
            viewer_user_id=viewer_user_id,
            page=page,
            per_page=per_page
        )

        return posts

    @staticmethod
    def pin_post(post_id: str, user_id: str) -> bool:
        """
        Pin post to profile top (unpin previous if exists)

        Args:
            post_id: Post ID
            user_id: User ID (must be post owner)

        Returns:
            True if pinned, False if failed
        """
        post = repos.social_posts.get_by_id(post_id)

        if not post or post['user_id'] != user_id:
            return False

        # Unpin previous pinned post
        repos.social_posts.unpin_all_for_user(user_id)

        # Pin this post
        return repos.social_posts.pin(post_id)

    @staticmethod
    def _handle_mentions(post_id: str, user_ids: List[str]):
        """Handle @mentions in post"""
        for mentioned_user_id in user_ids:
            repos.social_posts.add_mention(post_id, mentioned_user_id)

    @staticmethod
    def _handle_hashtags(post_id: str, hashtags: List[str]):
        """Handle hashtags in post"""
        for hashtag in hashtags:
            # Normalize hashtag (lowercase, remove #)
            normalized = hashtag.lower().strip('#')
            repos.social_posts.add_hashtag(post_id, normalized)
