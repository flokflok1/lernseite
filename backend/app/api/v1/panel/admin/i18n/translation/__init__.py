"""
i18n Translation API Module

Translation endpoints:
- AI Translation: POST /i18n/admin/ai/translate
- Bulk Translation: POST /i18n/admin/ai/translate/bulk
- Translation API: GET /translation/<namespace>/<key_path>/<language_code>
- Translation Jobs: GET /translation/job/<job_id>
"""

from .ai_translation import i18n_ai_translation_bp
from .translation_api import bp as translation_bp

__all__ = ['i18n_ai_translation_bp', 'translation_bp']
