"""
Admin Course AI Package

Course-specific AI configuration (ai_settings.py) and authoring (authoring.py).
Both are bridge modules that point to their standalone files.
"""

from app.api.admin.content_management.courses import ai_settings, authoring

__all__ = ['ai_settings', 'authoring']
