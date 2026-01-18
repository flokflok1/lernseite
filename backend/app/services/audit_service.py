"""
Audit Service Bridge - LEGACY IMPORT PATH

NOTICE: This file exists for backward compatibility only.
The actual implementation has been moved to app/services/system/audit/service.py

DEPRECATED IMPORT (old path - still works):
    from app.services.audit_service import AuditService, Severity

RECOMMENDED IMPORT (new path):
    from app.services.system.audit import AuditService

This bridge re-exports the AuditService class for backward compatibility
with existing code. All new code should use the recommended import path.
"""

# Re-export from the actual location for backward compatibility
from app.services.system.audit.service import AuditService, Severity

__all__ = ['AuditService', 'Severity']
