"""Backward Compatibility Bridge: audit_service
DEPRECATED: Use 'from app.application.services.system.audit import AuditService, Severity' instead
This bridge maintains backward compatibility with old import paths.
"""
from app.application.services.system.audit import AuditService, Severity
__all__ = ['AuditService', 'Severity']
