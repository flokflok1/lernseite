"""
LernsystemX Profile User Package

User profile management endpoints.

Endpoints:
- GET /api/v1/profile - Get current user profile
- PUT /api/v1/profile - Update current user profile
- POST /api/v1/profile/change-password - Change password
- DELETE /api/v1/profile - Delete own account (soft delete)
- GET /api/v1/profile/activity - Get user activity history
- GET /api/v1/profile/preferences - Get user preferences
- PUT /api/v1/profile/preferences - Update user preferences
"""

from .core import profile_core_bp
from .activity import profile_activity_bp
from .preferences import profile_preferences_bp

__all__ = ['profile_core_bp', 'profile_activity_bp', 'profile_preferences_bp']
