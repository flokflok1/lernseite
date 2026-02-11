"""
User Profiles System

Provides profile management and profile-related components.
"""

# Re-export from components
from app.domain.social.profiles.components import (
    AchievementsService,
    AvatarService,
    PortfolioService
)

# Re-export from management
from app.domain.social.profiles.management import ProfileManager

__all__ = [
    # Components
    'AchievementsService',
    'AvatarService',
    'PortfolioService',

    # Management
    'ProfileManager'
]
