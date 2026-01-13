"""
LernsystemX Profile Appearance Package

User appearance and theme settings.

Endpoints:
- GET /api/v1/profile/theme - Get current theme settings
- PUT /api/v1/profile/theme - Update theme settings
"""

from .theme import profile_theme_bp

__all__ = ['profile_theme_bp']
