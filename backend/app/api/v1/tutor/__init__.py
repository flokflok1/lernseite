"""
LernsystemX Tutor Module Orchestrator

Combines user-facing and admin tutor endpoints into a unified module.

Structure:
  - tutor_core.py: Shared components (value objects, enums, constants, helpers)
  - tutor_user.py: User endpoints (chat, TTS, voice listing)
  - tutor_admin.py: Admin endpoints (content generation)
  - __init__.py: Orchestrator (this file)

Blueprint Exports:
  - tutor_bp: User-facing tutor endpoints (POST /tutor/chat, etc.)
  - tutor_admin_bp: Admin tutor endpoints (POST /admin-panel/tutor/generate-*, etc.)
"""

from app.api.v1.tutor.tutor_user import tutor_bp
from app.api.v1.tutor.tutor_admin import tutor_admin_bp

__all__ = ['tutor_bp', 'tutor_admin_bp']
