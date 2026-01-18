"""
Legacy Service Bridges - Backward Compatibility

This package contains all backward-compatibility bridge files that maintain
old import paths to support gradual migration to the DDD architecture.

These bridges should NOT be imported directly. Instead, they are automatically
made available at the old paths via sys.modules injection.

Examples of old paths that still work:
  - from app.application.services.ai_adapter import AIAdapter
  - from app.application.services.i18n_service import I18nService
  - from app.application.services.audit_service import AuditService

All of these automatically redirect to their new domain-based locations.
"""
