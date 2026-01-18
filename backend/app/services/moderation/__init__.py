"""
Content Moderation Service

Handles course moderation and AI-assisted content analysis:
- Moderation workflow state machine
- AI-powered content analysis
- Rule enforcement and policies
- Moderation dashboard operations
"""

from .service import ModerationService

__all__ = [
    'ModerationService',
]
