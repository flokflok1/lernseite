"""
Audit Log Query Repository - Static query methods for audit logging.

Provides:
- Audit log insertion (used by AuditService)
- Audit log querying (user logs, failed logins, suspicious activity)
- Audit log helpers for group management services

Uses the static fetch_one/fetch_all/execute_query helpers.
"""

from typing import Optional, Dict, Any, List

from app.infrastructure.persistence.database.connection import execute_query, fetch_all


class AuditQueryRepository:
    """Static query methods for audit log operations."""

    @staticmethod
    def insert_audit_log(
        event_type: str,
        event_category: str,
        severity: str,
        user_id: Optional[int],
        user_email: Optional[str],
        user_role: Optional[str],
        session_id: Optional[str],
        ip_address: Optional[str],
        user_agent: Optional[str],
        resource_type: Optional[str],
        resource_id: Optional[str],
        action: str,
        description: Optional[str],
        metadata_json: Optional[str],
        success: bool,
        error_message: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Insert a new audit log entry.

        Args:
            event_type: Type of event
            event_category: Category of event
            severity: Severity level
            user_id: User ID (if authenticated)
            user_email: User email
            user_role: User role
            session_id: Session/JWT ID
            ip_address: Client IP address
            user_agent: Browser user agent
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            action: Action performed
            description: Human-readable description
            metadata_json: JSON-serialized metadata
            success: Whether action succeeded
            error_message: Error message if failed

        Returns:
            Dict with log_id or None on failure
        """
        return execute_query(
            """
            INSERT INTO core.audit_logs (
                event_type, event_category, severity,
                user_id, user_email, user_role,
                session_id, ip_address, user_agent,
                resource_type, resource_id,
                action, description, metadata,
                success, error_message
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s, %s,
                %s, %s
            )
            RETURNING log_id
            """,
            (
                event_type, event_category, severity,
                user_id, user_email, user_role,
                session_id, ip_address, user_agent,
                resource_type, resource_id,
                action, description, metadata_json,
                success, error_message
            ),
            fetch_one=True
        )

    @staticmethod
    def insert_simple_audit_log(
        user_id: str,
        action: str,
        description: str,
        metadata: str
    ) -> None:
        """
        Insert a simple audit log entry (used by group management services).

        Args:
            user_id: User ID performing the action
            action: Action identifier
            description: Human-readable description
            metadata: JSON string with additional context
        """
        execute_query(
            """
            INSERT INTO core.audit_logs (user_id, action, description, metadata)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, action, description, metadata)
        )

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
        return fetch_all(
            """
            SELECT *
            FROM audit_logs
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """,
            (user_id, limit, offset)
        )

    @staticmethod
    def get_failed_login_attempts(event_type: str, hours: int = 24) -> List[Dict]:
        """
        Get failed login attempts within the last N hours.

        Args:
            event_type: The login failed event type string
            hours: Number of hours to look back

        Returns:
            List of failed login attempts
        """
        return fetch_all(
            """
            SELECT *
            FROM audit_logs
            WHERE event_type = %s
              AND success = false
              AND created_at > NOW() - INTERVAL '%s hours'
            ORDER BY created_at DESC
            """,
            (event_type, hours)
        )

    @staticmethod
    def get_suspicious_activity(hours: int = 24, min_failures: int = 5) -> List[Dict]:
        """
        Get IPs with suspicious activity (multiple failures).

        Args:
            hours: Number of hours to look back
            min_failures: Minimum failure count to be considered suspicious

        Returns:
            List of (ip_address, failure_count, last_failure, attempted_emails)
        """
        return fetch_all(
            """
            SELECT
                ip_address,
                COUNT(*) as failure_count,
                MAX(created_at) as last_failure,
                ARRAY_AGG(DISTINCT user_email) as attempted_emails
            FROM audit_logs
            WHERE success = false
              AND created_at > NOW() - INTERVAL '%s hours'
            GROUP BY ip_address
            HAVING COUNT(*) >= %s
            ORDER BY failure_count DESC
            """,
            (hours, min_failures)
        )
