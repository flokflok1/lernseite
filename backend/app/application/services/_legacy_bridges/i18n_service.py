"""
Backward Compatibility Bridge: i18n_service

DEPRECATED: Use 'from app.application.services.i18n.legacy import I18nService' instead
This bridge maintains backward compatibility with old import paths.
"""

from app.application.services.i18n.legacy import (
    I18nService,
    I18nImportService,
    I18nSyncService,
    I18nSyncAnalyticsService,
    I18nSyncApplyService,
)

__all__ = [
    'I18nService',
    'I18nImportService',
    'I18nSyncService',
    'I18nSyncAnalyticsService',
    'I18nSyncApplyService',
]
