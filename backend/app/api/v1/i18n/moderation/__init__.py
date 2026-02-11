"""
i18n Moderation API Module

Moderation endpoints:
- Moderation Dashboard: GET /i18n/admin/moderation/dashboard
- Review Queue: GET /i18n/admin/moderation/queue
- AI Review: POST /i18n/admin/moderation/ai-review
- Translation Suggestions: POST /i18n/suggestions
- Configuration: GET/PUT /i18n/admin/config
"""

from .moderation import i18n_moderation_bp
from .suggestions import i18n_suggestions_bp

__all__ = ['i18n_moderation_bp', 'i18n_suggestions_bp']
