"""
i18n Legacy Services Package

Backward compatibility layer for original i18n services.
These have been consolidated from root-level modules.

Modules:
  - service: Core I18nService class
  - import_service: Translation import operations
  - sync_service: Translation synchronization core
  - sync_analytics: Sync analytics and reporting
  - sync_apply: Sync application/deployment
"""

from .service import I18nService
from .import_service import I18nImportService
from .sync_service import I18nSyncService
from .sync_analytics import I18nSyncAnalyticsService
from .sync_apply import I18nSyncApplyService

__all__ = [
    'I18nService',
    'I18nImportService',
    'I18nSyncService',
    'I18nSyncAnalyticsService',
    'I18nSyncApplyService',
]
