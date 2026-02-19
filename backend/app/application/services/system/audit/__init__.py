"""
Audit & Compliance Services

System-wide audit logging:
- Audit trail recording
- Compliance monitoring
- Event tracking and analysis
- Query and reporting (service_part2)
"""

from .service import AuditService, EventCategory, EventType, Severity
from .service_part2 import *  # noqa: F401,F403 - Attaches query methods to AuditService

__all__ = [
    'AuditService',
    'EventCategory',
    'EventType',
    'Severity',
]
