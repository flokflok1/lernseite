"""
LernsystemX - Audit Logging Service

Based on Dok 31 (Security Architecture) and Phase 20 requirements.

Provides centralized audit logging for security events:
- Authentication events (login, logout, 2FA, password reset)
- Authorization events (permission denied, role changes)
- Data access events (view, export sensitive data)
- Data modification events (create, update, delete)
- Admin actions (user management, system configuration)

ISO 27001:2013 compliant - Audit Logging & Monitoring
DSGVO/GDPR compliant - Activity Tracking & Transparency
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from flask import request, g, current_app
import json

from app.database.connection import execute_query, fetch_all, fetch_one


# ==========================================
# EVENT TYPES & CATEGORIES
# ==========================================

class EventType:
    """Audit event types"""
    # Authentication
    LOGIN = 'login'
    LOGOUT = 'logout'
    LOGIN_FAILED = 'login_failed'
    REGISTER = 'register'
    PASSWORD_RESET_REQUEST = 'password_reset_request'
    PASSWORD_RESET = 'password_reset'
    PASSWORD_CHANGE = 'password_change'
    EMAIL_VERIFY = 'email_verify'
    TWO_FACTOR_ENABLE = '2fa_enable'
    TWO_FACTOR_DISABLE = '2fa_disable'
    TWO_FACTOR_VERIFY = '2fa_verify'
    TWO_FACTOR_FAILED = '2fa_failed'

    # Authorization
    PERMISSION_DENIED = 'permission_denied'
    ROLE_CHANGE = 'role_change'
    ACCESS_GRANTED = 'access_granted'

    # Data Operations
    CREATE = 'create'
    READ = 'read'
    UPDATE = 'update'
    DELETE = 'delete'
    EXPORT = 'export'

    # Admin Actions
    USER_CREATED = 'user_created'
    USER_UPDATED = 'user_updated'
    USER_DELETED = 'user_deleted'
    USER_DEACTIVATED = 'user_deactivated'
    USER_ACTIVATED = 'user_activated'
    ORG_CREATED = 'org_created'
    ORG_UPDATED = 'org_updated'
    ORG_DELETED = 'org_deleted'
    CONFIG_CHANGED = 'config_changed'

    # System Events
    SYSTEM_ERROR = 'system_error'
    RATE_LIMIT_EXCEEDED = 'rate_limit_exceeded'
    ACCOUNT_LOCKED = 'account_locked'
    SUSPICIOUS_ACTIVITY = 'suspicious_activity'


class EventCategory:
    """Audit event categories"""
    AUTHENTICATION = 'authentication'
    AUTHORIZATION = 'authorization'
    DATA_ACCESS = 'data_access'
    DATA_MODIFICATION = 'data_modification'
    ADMIN_ACTION = 'admin_action'
    SYSTEM = 'system'


class Severity:
    """Log severity levels"""
    DEBUG = 'debug'
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    CRITICAL = 'critical'


# ==========================================
# AUDIT SERVICE
# ==========================================

class AuditService:
    """
    Centralized audit logging service.

    Thread-safe service for logging security events to the audit_logs table.
    Automatically captures request context (IP, user agent, session).
    """

    @staticmethod
    def log_event(
        event_type: str,
        event_category: str,
        action: str,
        severity: str = Severity.INFO,
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
        user_role: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Optional[int]:
        """
        Log a security event to the audit log.

        Args:
            event_type: Type of event (from EventType)
            event_category: Category (from EventCategory)
            action: Action performed (human-readable)
            severity: Severity level (from Severity)
            user_id: User ID (if authenticated)
            user_email: User email (for failed logins where user_id is None)
            user_role: User role
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            description: Human-readable description
            metadata: Additional context (will be JSON-serialized)
            success: Whether action succeeded
            error_message: Error message if failed
            ip_address: Client IP (auto-detected if None)
            user_agent: User agent (auto-detected if None)
            session_id: Session/JWT ID (auto-detected if None)

        Returns:
            log_id of created audit log entry, or None if logging failed
        """
        # Skip if audit logging is disabled
        if not current_app.config.get('AUDIT_LOG_ENABLED', True):
            return None

        try:
            # Auto-detect request context if not provided
            if request:
                if ip_address is None:
                    ip_address = AuditService._get_client_ip()
                if user_agent is None:
                    user_agent = request.headers.get('User-Agent', 'Unknown')
                if session_id is None:
                    session_id = AuditService._get_session_id()

            # Try to get current user from Flask context if not provided
            if user_id is None and hasattr(g, 'current_user') and g.current_user:
                user_id = g.current_user.get('user_id')
                user_email = user_email or g.current_user.get('email')
                user_role = user_role or g.current_user.get('role')

            # Sanitize metadata (remove sensitive fields)
            if metadata:
                metadata = AuditService._sanitize_metadata(metadata)

            # Insert audit log
            result = execute_query(
                """
                INSERT INTO audit_logs (
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
                    action, description, json.dumps(metadata) if metadata else None,
                    success, error_message
                ),
                fetch_one=True
            )

            if result:
                return result['log_id']  # Return log_id from dict

        except Exception as e:
            # Log audit failures to application log, but don't raise
            # to prevent audit logging from breaking application flow
            current_app.logger.error(f"Failed to write audit log: {str(e)}")

        return None

    @staticmethod
    def _get_client_ip() -> str:
        """Get real client IP address (handles proxies)"""
        # Check X-Forwarded-For header (reverse proxy)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            # Take first IP (client IP)
            return forwarded_for.split(',')[0].strip()

        # Check X-Real-IP header (Nginx)
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip

        # Fallback to direct IP
        return request.remote_addr or 'unknown'

    @staticmethod
    def _get_session_id() -> Optional[str]:
        """Get session ID from JWT or session"""
        # Try to get JWT jti
        if hasattr(g, 'jwt_payload'):
            return g.jwt_payload.get('jti')

        # Try to get session ID
        from flask import session
        return session.get('session_id')

    @staticmethod
    def _sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove sensitive fields from metadata before logging.

        Prevents passwords, tokens, secrets from being logged.

        Args:
            metadata: Original metadata dict

        Returns:
            Sanitized metadata dict
        """
        sensitive_keys = {
            'password', 'passwd', 'pwd',
            'secret', 'token', 'api_key', 'apikey',
            'private_key', 'privatekey',
            'credit_card', 'creditcard', 'cvv',
            'ssn', 'social_security',
            'two_factor_secret', 'totp_secret'
        }

        sanitized = {}
        for key, value in metadata.items():
            # Check if key contains sensitive terms (case-insensitive)
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = '***REDACTED***'
            elif isinstance(value, dict):
                # Recursively sanitize nested dicts
                sanitized[key] = AuditService._sanitize_metadata(value)
            else:
                sanitized[key] = value

        return sanitized

    # ==========================================
    # CONVENIENCE METHODS FOR COMMON EVENTS
    # ==========================================

    @staticmethod
    def log_login_success(user_id: int, user_email: str, user_role: str, metadata: Optional[Dict] = None):
        """Log successful login"""
        return AuditService.log_event(
            event_type=EventType.LOGIN,
            event_category=EventCategory.AUTHENTICATION,
            action='login_success',
            severity=Severity.INFO,
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            description=f'User {user_email} logged in successfully',
            metadata=metadata,
            success=True
        )

    @staticmethod
    def log_login_failed(email: str, reason: str, metadata: Optional[Dict] = None):
        """Log failed login attempt"""
        return AuditService.log_event(
            event_type=EventType.LOGIN_FAILED,
            event_category=EventCategory.AUTHENTICATION,
            action='login_failed',
            severity=Severity.WARNING,
            user_email=email,
            description=f'Failed login attempt for {email}',
            metadata=metadata,
            success=False,
            error_message=reason
        )

    @staticmethod
    def log_logout(user_id: int, user_email: str):
        """Log user logout"""
        return AuditService.log_event(
            event_type=EventType.LOGOUT,
            event_category=EventCategory.AUTHENTICATION,
            action='logout',
            severity=Severity.INFO,
            user_id=user_id,
            user_email=user_email,
            description=f'User {user_email} logged out',
            success=True
        )

    @staticmethod
    def log_permission_denied(user_id: int, user_email: str, permission: str, resource: str):
        """Log permission denied event"""
        return AuditService.log_event(
            event_type=EventType.PERMISSION_DENIED,
            event_category=EventCategory.AUTHORIZATION,
            action='permission_denied',
            severity=Severity.WARNING,
            user_id=user_id,
            user_email=user_email,
            description=f'Permission denied: {permission} on {resource}',
            metadata={'permission': permission, 'resource': resource},
            success=False,
            error_message=f'Missing permission: {permission}'
        )

    @staticmethod
    def log_2fa_enabled(user_id: int, user_email: str):
        """Log 2FA enabled"""
        return AuditService.log_event(
            event_type=EventType.TWO_FACTOR_ENABLE,
            event_category=EventCategory.AUTHENTICATION,
            action='2fa_enabled',
            severity=Severity.INFO,
            user_id=user_id,
            user_email=user_email,
            description=f'Two-factor authentication enabled for {user_email}',
            success=True
        )

    @staticmethod
    def log_2fa_disabled(user_id: int, user_email: str):
        """Log 2FA disabled"""
        return AuditService.log_event(
            event_type=EventType.TWO_FACTOR_DISABLE,
            event_category=EventCategory.AUTHENTICATION,
            action='2fa_disabled',
            severity=Severity.WARNING,
            user_id=user_id,
            user_email=user_email,
            description=f'Two-factor authentication disabled for {user_email}',
            success=True
        )

    @staticmethod
    def log_account_locked(email: str, reason: str):
        """Log account lockout"""
        return AuditService.log_event(
            event_type=EventType.ACCOUNT_LOCKED,
            event_category=EventCategory.AUTHENTICATION,
            action='account_locked',
            severity=Severity.WARNING,
            user_email=email,
            description=f'Account locked for {email}: {reason}',
            success=True
        )

    @staticmethod
    def log_rate_limit_exceeded(endpoint: str, limit: str):
        """Log rate limit exceeded"""
        return AuditService.log_event(
            event_type=EventType.RATE_LIMIT_EXCEEDED,
            event_category=EventCategory.SYSTEM,
            action='rate_limit_exceeded',
            severity=Severity.WARNING,
            description=f'Rate limit exceeded for endpoint: {endpoint}',
            metadata={'endpoint': endpoint, 'limit': limit},
            success=False,
            error_message=f'Rate limit {limit} exceeded'
        )

    @staticmethod
    def log_action(
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = 'info'
    ):
        """
        Convenience method for logging admin actions.

        Wrapper around log_event() with admin-specific defaults.

        Args:
            user_id: Admin user ID performing the action
            action: Action name (e.g., 'admin.users.ban')
            resource_type: Type of resource (e.g., 'user', 'course')
            resource_id: ID of the resource affected
            details: Additional context
            severity: Severity level (info, warning, high, critical)

        Returns:
            log_id of created audit log entry
        """
        # Map severity levels
        severity_map = {
            'info': Severity.INFO,
            'warning': Severity.WARNING,
            'medium': Severity.WARNING,
            'high': Severity.ERROR,
            'critical': Severity.CRITICAL
        }

        mapped_severity = severity_map.get(severity.lower(), Severity.INFO)

        # Determine event category based on action
        if action.startswith('admin.'):
            event_category = EventCategory.ADMIN_ACTION
        elif 'delete' in action or 'update' in action or 'create' in action:
            event_category = EventCategory.DATA_MODIFICATION
        elif 'view' in action or 'list' in action or 'read' in action:
            event_category = EventCategory.DATA_ACCESS
        else:
            event_category = EventCategory.SYSTEM

        return AuditService.log_event(
            event_type=action,
            event_category=event_category,
            action=action,
            severity=mapped_severity,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            description=f'Admin action: {action} on {resource_type}',
            metadata=details,
            success=True
        )

    # ==========================================
    # QUERY METHODS
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
    def get_failed_login_attempts(hours: int = 24) -> List[Dict]:
        """
        Get failed login attempts within the last N hours.

        Args:
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
            (EventType.LOGIN_FAILED, hours)
        )

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


# ==========================================
# EXPORTS
# ==========================================

__all__ = [
    'AuditService',
    'EventType',
    'EventCategory',
    'Severity',
]
