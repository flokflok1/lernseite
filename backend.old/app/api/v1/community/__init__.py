"""
Community API Package

Blueprints (must be registered with api_v1):
- forums_bp - Community Forums - /community/forums
- groups_bp - Study Groups - /community/groups

Registration: Blueprints are registered in app/api/__init__.py after api_v1 creation.
"""

from app.api.community.forums import forums_bp
from app.api.community.groups import groups_bp

__all__ = ['forums_bp', 'groups_bp']
