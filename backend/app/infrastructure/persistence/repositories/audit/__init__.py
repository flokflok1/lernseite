"""
Audit Repository Module

Provides repositories for audit logging.

Classes:
    - AuditLogRepository: Instance-based audit log CRUD (psycopg3 connection)
    - AuditQueryRepository: Static query methods for audit log operations
"""

from app.infrastructure.persistence.repositories.audit.log import AuditLogRepository
from app.infrastructure.persistence.repositories.audit.queries import AuditQueryRepository

__all__ = [
    'AuditLogRepository',
    'AuditQueryRepository',
]
