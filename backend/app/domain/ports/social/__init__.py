"""
Social Domain Ports

Provides abstract interfaces for social network domain operations.
"""

from app.domain.ports.social.ports import (
    SocialPostsPort,
    SocialLikesPort,
    SocialCommentsPort,
    SocialFollowsPort,
    SocialNotificationsPort
)

__all__ = [
    'SocialPostsPort',
    'SocialLikesPort',
    'SocialCommentsPort',
    'SocialFollowsPort',
    'SocialNotificationsPort'
]
