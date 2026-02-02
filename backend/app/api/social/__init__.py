"""
Social API Module

All social endpoints are feature-flagged for progressive rollout.

Blueprints (must be registered with api_v1):
- posts_bp - User Posts (@require_feature('user_posts')) - /social/posts
- feed_bp - Feed System (@require_feature('feed_system')) - /social/feed
- follow_bp - Follow System (@require_feature('follow_system')) - /social/follow
- likes_bp - Likes & Reactions (@require_feature('likes_reactions')) - /social/likes
- comments_bp - Comments (@require_feature('comments')) - /social/comments

Note: All endpoints are feature-flagged. Disabled features will return 403.
Registration: Blueprints are registered in app/api/__init__.py after api_v1 creation.
"""

from app.api.social.posts import posts_bp
from app.api.social.feed import feed_bp
from app.api.social.follow import follow_bp
from app.api.social.likes import likes_bp
from app.api.social.comments import comments_bp

__all__ = [
    'posts_bp',
    'feed_bp',
    'follow_bp',
    'likes_bp',
    'comments_bp'
]
