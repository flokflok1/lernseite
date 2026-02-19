"""
LernsystemX - Audit Logging Service (Part 2)

Query and reporting methods for the AuditService.

Provides methods for:
- Querying user audit logs
- Retrieving failed login attempts
- Detecting suspicious activity patterns
"""

from typing import Dict, List

from app.infrastructure.persistence.repositories.audit.queries import AuditQueryRepository

from .service import AuditService, EventType


# ==========================================
# QUERY METHODS (extend AuditService)
# ==========================================


@staticmethod
def get_user_audit_logs(user_id: int, limit: int = 100, offset: int = 0) -> List[Dict]:
    """
    Get audit logs for a specific user.

    Args:
        user_id: User ID
        limit: Maximum number of results
        offset: Pagination offset

    Returns:
        List of audit log entries
    """
    return AuditQueryRepository.get_user_audit_logs(user_id, limit, offset)


@staticmethod
def get_failed_login_attempts(hours: int = 24) -> List[Dict]:
    """
    Get failed login attempts within the last N hours.

    Args:
        hours: Number of hours to look back

    Returns:
        List of failed login attempts
    """
    return AuditQueryRepository.get_failed_login_attempts(EventType.LOGIN_FAILED, hours)


@staticmethod
def get_suspicious_activity(hours: int = 24, min_failures: int = 5) -> List[Dict]:
    """
    Get IPs with suspicious activity (multiple failures).

    Args:
        hours: Number of hours to look back
        min_failures: Minimum failure count to be considered suspicious

    Returns:
        List of (ip_address, failure_count, last_failure)
    """
    return AuditQueryRepository.get_suspicious_activity(hours, min_failures)


# Attach query methods to AuditService class
AuditService.get_user_audit_logs = get_user_audit_logs
AuditService.get_failed_login_attempts = get_failed_login_attempts
AuditService.get_suspicious_activity = get_suspicious_activity


__all__ = [
    'AuditService',
]
