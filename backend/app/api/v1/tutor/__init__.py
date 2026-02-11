"""
LernsystemX Tutor Module Orchestrator

Combines user-facing and admin tutor endpoints into a unified module.

Structure:
  - interfaces/: Organized tutor functionality
    - admin.py: Admin endpoints (content generation)
    - core.py: Shared components (value objects, enums, constants, helpers)
    - user.py: User endpoints (chat, TTS, voice listing)
  - __init__.py: Orchestrator (this file)

Blueprint Exports:
  - tutor_bp: User-facing tutor endpoints (POST /tutor/chat, etc.)
  - tutor_admin_bp: Admin tutor endpoints (POST /admin-panel/tutor/generate-*, etc.)
"""

from app.api.v1.tutor.interfaces import tutor_bp, tutor_admin_bp

__all__ = ['tutor_bp', 'tutor_admin_bp']
