"""
Community API Package

Blueprints (must be registered with api_v1):
- forums_bp - Community Forums - /community/forums
- groups_bp - Study Groups - /community/groups

Registration: Blueprints are registered in app/api/__init__.py after api_v1 creation.

Note: groups_part2 registers membership and permission routes on groups_bp.
"""

from app.api.v1.community.forums import forums_bp
from app.api.v1.community.groups import groups_bp
import app.api.v1.community.groups_part2  # noqa: F401 - registers routes on groups_bp

__all__ = ['forums_bp', 'groups_bp']
