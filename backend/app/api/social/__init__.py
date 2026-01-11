"""
Social API Module

All social endpoints are feature-flagged for progressive rollout.

Blueprints:
- posts_bp - User Posts (@require_feature('user_posts'))
- feed_bp - Feed System (@require_feature('feed_system'))
- follow_bp - Follow System (@require_feature('follow_system'))
- likes_bp - Likes & Reactions (@require_feature('likes_reactions'))
- comments_bp - Comments (@require_feature('comments'))

Usage:
    from app.api.social import register_social_blueprints

    register_social_blueprints(app)
"""

from flask import Flask
from app.api.social.posts import posts_bp
from app.api.social.feed import feed_bp
from app.api.social.follow import follow_bp
from app.api.social.likes import likes_bp
from app.api.social.comments import comments_bp


def register_social_blueprints(app: Flask):
    """
    Register all social blueprints with the Flask app

    Args:
        app: Flask application instance

    Note:
        All endpoints are feature-flagged. Disabled features will return 403.
    """
    app.register_blueprint(posts_bp)
    app.register_blueprint(feed_bp)
    app.register_blueprint(follow_bp)
    app.register_blueprint(likes_bp)
    app.register_blueprint(comments_bp)


__all__ = [
    'register_social_blueprints',
    'posts_bp',
    'feed_bp',
    'follow_bp',
    'likes_bp',
    'comments_bp'
]
