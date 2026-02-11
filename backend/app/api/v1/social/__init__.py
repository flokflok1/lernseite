"""
Social API Package

Social network features with posts, feed, follows, likes, and comments.

Structure:
- user/ - User social endpoints (posts, feed, follow, likes, comments)

Consolidated from: social/ root files (Batch 5, Phase 7)

All endpoints are feature-flagged for progressive rollout (@require_feature):
- /social/posts - User Posts (@require_feature('user_posts'))
- /social/feed - Feed System (@require_feature('feed_system'))
- /social/follow - Follow System (@require_feature('follow_system'))
- /social/likes - Likes & Reactions (@require_feature('likes_reactions'))
- /social/comments - Comments (@require_feature('comments'))

All endpoints require authentication (@token_required) + feature flag check
Disabled features return 403 Forbidden
"""

from app.api.v1.social.user.posts import posts_bp
from app.api.v1.social.user.feed import feed_bp
from app.api.v1.social.user.follow import follow_bp
from app.api.v1.social.user.likes import likes_bp
from app.api.v1.social.user.comments import comments_bp

__all__ = [
    'posts_bp',
    'feed_bp',
    'follow_bp',
    'likes_bp',
    'comments_bp'
]
