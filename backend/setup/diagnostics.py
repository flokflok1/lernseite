"""
LernsystemX Setup - Diagnostics

System diagnostics for health checks, configuration validation, and component status.

Provides:
- Individual component checks (DB, Redis, AI Keys, Email, Storage, Monitoring, Security)
- Aggregated diagnostics report
- Light vs. full diagnostic modes
- Auto-fix suggestions

Phase 23 - Setup Wizard Erweiterungen
"""

from typing import Literal, Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import os


@dataclass
class DiagnosticCheckResult:
    """Result of a single diagnostic check"""
    name: str
    status: Literal["ok", "warn", "fail"]
    message: str
    details: Optional[Dict[str, Any]] = None
    auto_fix_available: bool = False
    auto_fix_description: Optional[str] = None


@dataclass
class DiagnosticsReport:
    """Aggregated diagnostics report"""
    overall_status: Literal["ok", "warn", "fail"]
    checks: List[DiagnosticCheckResult]
    timestamp: str
    total_checks: int
    passed: int
    warnings: int
    failed: int


class SystemDiagnostics:
    """
    System diagnostics runner for LernsystemX.

    Performs comprehensive health checks across all system components.
    """

    @staticmethod
    def check_database_connection() -> DiagnosticCheckResult:
        """
        Check PostgreSQL database connectivity and configuration.

        Returns:
            DiagnosticCheckResult with connection status
        """
        try:
            from app.extensions import db_pool

            if db_pool is None:
                return DiagnosticCheckResult(
                    name="Database Connection",
                    status="fail",
                    message="Database pool not initialized",
                    details={"error": "db_pool is None"},
                    auto_fix_available=False
                )

            # Test connection
            with db_pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT version();")
                    version = cur.fetchone()[0]

                    # Check for migration history table
                    cur.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables
                            WHERE table_name = 'migration_history'
                        );
                    """)
                    has_migration_table = cur.fetchone()[0]

                    return DiagnosticCheckResult(
                        name="Database Connection",
                        status="ok",
                        message="Database connection successful",
                        details={
                            "version": version,
                            "has_migration_table": has_migration_table,
                            "pool_size": db_pool.get_stats().get('pool_size', 'unknown')
                        }
                    )

        except Exception as e:
            return DiagnosticCheckResult(
                name="Database Connection",
                status="fail",
                message=f"Database connection failed: {str(e)}",
                details={"error": str(e)},
                auto_fix_available=False
            )

    @staticmethod
    def check_redis_connection() -> DiagnosticCheckResult:
        """
        Check Redis connectivity and configuration.

        Returns:
            DiagnosticCheckResult with Redis status
        """
        try:
            from app.extensions import redis_client

            if redis_client is None:
                return DiagnosticCheckResult(
                    name="Redis Connection",
                    status="fail",
                    message="Redis client not initialized",
                    details={"error": "redis_client is None"},
                    auto_fix_available=False
                )

            # Test connection
            redis_client.ping()

            # Get info
            info = redis_client.info()

            return DiagnosticCheckResult(
                name="Redis Connection",
                status="ok",
                message="Redis connection successful",
                details={
                    "version": info.get('redis_version'),
                    "used_memory_human": info.get('used_memory_human'),
                    "connected_clients": info.get('connected_clients')
                }
            )

        except Exception as e:
            return DiagnosticCheckResult(
                name="Redis Connection",
                status="fail",
                message=f"Redis connection failed: {str(e)}",
                details={"error": str(e)},
                auto_fix_available=False
            )

    @staticmethod
    def check_ai_keys() -> DiagnosticCheckResult:
        """
        Check if AI API keys are configured.

        Returns:
            DiagnosticCheckResult with AI keys status
        """
        from flask import current_app

        keys_configured = {
            "openai": bool(current_app.config.get('OPENAI_API_KEY')),
            "anthropic": bool(current_app.config.get('ANTHROPIC_API_KEY')),
            "google": bool(current_app.config.get('GOOGLE_API_KEY'))
        }

        configured_count = sum(keys_configured.values())

        if configured_count == 0:
            return DiagnosticCheckResult(
                name="AI API Keys",
                status="fail",
                message="No AI API keys configured",
                details=keys_configured,
                auto_fix_available=False,
                auto_fix_description="Configure at least one AI provider key in /setup/ki-config"
            )
        elif configured_count < 2:
            return DiagnosticCheckResult(
                name="AI API Keys",
                status="warn",
                message=f"Only {configured_count}/3 AI providers configured",
                details=keys_configured,
                auto_fix_available=False,
                auto_fix_description="Consider configuring backup AI providers"
            )
        else:
            return DiagnosticCheckResult(
                name="AI API Keys",
                status="ok",
                message=f"{configured_count}/3 AI providers configured",
                details=keys_configured
            )

    @staticmethod
    def check_email_config() -> DiagnosticCheckResult:
        """
        Check email configuration (SMTP settings).

        Returns:
            DiagnosticCheckResult with email config status
        """
        from flask import current_app

        required_settings = {
            "MAIL_SERVER": current_app.config.get('MAIL_SERVER'),
            "MAIL_PORT": current_app.config.get('MAIL_PORT'),
            "MAIL_USERNAME": current_app.config.get('MAIL_USERNAME'),
            "MAIL_PASSWORD": bool(current_app.config.get('MAIL_PASSWORD')),  # Don't expose password
            "MAIL_DEFAULT_SENDER": current_app.config.get('MAIL_DEFAULT_SENDER')
        }

        missing = [k for k, v in required_settings.items() if not v]

        if len(missing) == len(required_settings):
            return DiagnosticCheckResult(
                name="Email Configuration",
                status="warn",
                message="Email not configured (optional for development)",
                details={"configured": False},
                auto_fix_available=False
            )
        elif missing:
            return DiagnosticCheckResult(
                name="Email Configuration",
                status="warn",
                message=f"Incomplete email configuration: {', '.join(missing)}",
                details={"missing": missing},
                auto_fix_available=False
            )
        else:
            return DiagnosticCheckResult(
                name="Email Configuration",
                status="ok",
                message="Email fully configured",
                details={"configured": True}
            )

    @staticmethod
    def check_backup_config() -> DiagnosticCheckResult:
        """
        Check backup configuration (Phase 18).

        Returns:
            DiagnosticCheckResult with backup config status
        """
        from flask import current_app

        backup_enabled = current_app.config.get('BACKUP_ENABLED', False)
        backup_path = current_app.config.get('BACKUP_PATH', '/var/backups/lsx')

        if not backup_enabled:
            return DiagnosticCheckResult(
                name="Backup Configuration",
                status="warn",
                message="Backups not enabled (recommended for production)",
                details={
                    "enabled": False,
                    "path": backup_path
                },
                auto_fix_available=False,
                auto_fix_description="Enable backups in production config"
            )

        # Check if backup directory exists and is writable
        if not os.path.exists(backup_path):
            return DiagnosticCheckResult(
                name="Backup Configuration",
                status="warn",
                message=f"Backup directory does not exist: {backup_path}",
                details={
                    "enabled": True,
                    "path": backup_path,
                    "exists": False
                },
                auto_fix_available=True,
                auto_fix_description=f"Create backup directory: {backup_path}"
            )

        if not os.access(backup_path, os.W_OK):
            return DiagnosticCheckResult(
                name="Backup Configuration",
                status="fail",
                message=f"Backup directory not writable: {backup_path}",
                details={
                    "enabled": True,
                    "path": backup_path,
                    "exists": True,
                    "writable": False
                },
                auto_fix_available=False
            )

        return DiagnosticCheckResult(
            name="Backup Configuration",
            status="ok",
            message="Backup configuration valid",
            details={
                "enabled": True,
                "path": backup_path,
                "exists": True,
                "writable": True
            }
        )

    @staticmethod
    def check_monitoring_config() -> DiagnosticCheckResult:
        """
        Check monitoring configuration (Phase 19).

        Returns:
            DiagnosticCheckResult with monitoring config status
        """
        from flask import current_app

        monitoring_enabled = current_app.config.get('MONITORING_ENABLED', False)
        metrics_path = current_app.config.get('MONITORING_METRICS_PATH', '/metrics')

        if not monitoring_enabled:
            return DiagnosticCheckResult(
                name="Monitoring Configuration",
                status="warn",
                message="Monitoring not enabled (recommended for production)",
                details={
                    "enabled": False,
                    "metrics_path": metrics_path
                },
                auto_fix_available=False,
                auto_fix_description="Enable monitoring in production config"
            )

        return DiagnosticCheckResult(
            name="Monitoring Configuration",
            status="ok",
            message="Monitoring enabled",
            details={
                "enabled": True,
                "metrics_path": metrics_path,
                "prometheus": current_app.config.get('PROMETHEUS_ENABLED', False)
            }
        )

    @staticmethod
    def check_security_config() -> DiagnosticCheckResult:
        """
        Check security configuration (Phase 20).

        Returns:
            DiagnosticCheckResult with security config status
        """
        from flask import current_app

        security_checks = {
            "secret_key_set": bool(current_app.config.get('SECRET_KEY')) and
                              len(current_app.config.get('SECRET_KEY', '')) >= 32,
            "jwt_secret_set": bool(current_app.config.get('JWT_SECRET_KEY')) and
                             len(current_app.config.get('JWT_SECRET_KEY', '')) >= 32,
            "rate_limiting_enabled": current_app.config.get('RATELIMIT_ENABLED', False),
            "rbac_enabled": current_app.config.get('RBAC_ENABLED', True),
            "https_only": current_app.config.get('SESSION_COOKIE_SECURE', False),
            "csrf_enabled": current_app.config.get('WTF_CSRF_ENABLED', True)
        }

        failed = [k for k, v in security_checks.items() if not v]

        if failed:
            status = "fail" if "secret_key_set" in failed or "jwt_secret_set" in failed else "warn"
            return DiagnosticCheckResult(
                name="Security Configuration",
                status=status,
                message=f"Security issues found: {', '.join(failed)}",
                details=security_checks,
                auto_fix_available=False
            )

        return DiagnosticCheckResult(
            name="Security Configuration",
            status="ok",
            message="All security checks passed",
            details=security_checks
        )

    @staticmethod
    def check_storage_config() -> DiagnosticCheckResult:
        """
        Check storage configuration (uploads, media).

        Returns:
            DiagnosticCheckResult with storage config status
        """
        from flask import current_app

        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')

        if not os.path.exists(upload_folder):
            return DiagnosticCheckResult(
                name="Storage Configuration",
                status="warn",
                message=f"Upload directory does not exist: {upload_folder}",
                details={
                    "upload_folder": upload_folder,
                    "exists": False
                },
                auto_fix_available=True,
                auto_fix_description=f"Create upload directory: {upload_folder}"
            )

        if not os.access(upload_folder, os.W_OK):
            return DiagnosticCheckResult(
                name="Storage Configuration",
                status="fail",
                message=f"Upload directory not writable: {upload_folder}",
                details={
                    "upload_folder": upload_folder,
                    "exists": True,
                    "writable": False
                },
                auto_fix_available=False
            )

        return DiagnosticCheckResult(
            name="Storage Configuration",
            status="ok",
            message="Storage configuration valid",
            details={
                "upload_folder": upload_folder,
                "exists": True,
                "writable": True
            }
        )

    @staticmethod
    def check_celery_config() -> DiagnosticCheckResult:
        """
        Check Celery/background task configuration.

        Returns:
            DiagnosticCheckResult with Celery status
        """
        from flask import current_app

        broker_url = current_app.config.get('CELERY_BROKER_URL')
        result_backend = current_app.config.get('CELERY_RESULT_BACKEND')

        if not broker_url:
            return DiagnosticCheckResult(
                name="Celery Configuration",
                status="fail",
                message="Celery broker not configured",
                details={
                    "broker_url": None,
                    "result_backend": result_backend
                },
                auto_fix_available=False
            )

        # Try to ping Celery broker (Redis)
        try:
            from app.extensions import redis_client
            redis_client.ping()

            return DiagnosticCheckResult(
                name="Celery Configuration",
                status="ok",
                message="Celery configuration valid",
                details={
                    "broker_configured": True,
                    "result_backend_configured": bool(result_backend),
                    "broker_accessible": True
                }
            )
        except Exception as e:
            return DiagnosticCheckResult(
                name="Celery Configuration",
                status="warn",
                message=f"Celery broker not accessible: {str(e)}",
                details={
                    "broker_configured": True,
                    "broker_accessible": False,
                    "error": str(e)
                }
            )

    @staticmethod
    def run_all_diagnostics(quick: bool = False) -> DiagnosticsReport:
        """
        Run all diagnostic checks and aggregate results.

        Args:
            quick: If True, skip time-consuming checks

        Returns:
            DiagnosticsReport with aggregated results
        """
        checks: List[DiagnosticCheckResult] = []

        # Core checks (always run)
        checks.append(SystemDiagnostics.check_database_connection())
        checks.append(SystemDiagnostics.check_redis_connection())
        checks.append(SystemDiagnostics.check_security_config())

        if not quick:
            # Extended checks (skip in quick mode)
            checks.append(SystemDiagnostics.check_ai_keys())
            checks.append(SystemDiagnostics.check_email_config())
            checks.append(SystemDiagnostics.check_backup_config())
            checks.append(SystemDiagnostics.check_monitoring_config())
            checks.append(SystemDiagnostics.check_storage_config())
            checks.append(SystemDiagnostics.check_celery_config())

        # Calculate statistics
        passed = sum(1 for c in checks if c.status == "ok")
        warnings = sum(1 for c in checks if c.status == "warn")
        failed = sum(1 for c in checks if c.status == "fail")

        # Determine overall status
        if failed > 0:
            overall_status = "fail"
        elif warnings > 0:
            overall_status = "warn"
        else:
            overall_status = "ok"

        return DiagnosticsReport(
            overall_status=overall_status,
            checks=checks,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            total_checks=len(checks),
            passed=passed,
            warnings=warnings,
            failed=failed
        )

    @staticmethod
    def get_report_dict(report: DiagnosticsReport) -> Dict[str, Any]:
        """
        Convert DiagnosticsReport to dictionary for JSON serialization.

        Args:
            report: DiagnosticsReport instance

        Returns:
            Dictionary representation
        """
        return {
            "overall_status": report.overall_status,
            "checks": [asdict(check) for check in report.checks],
            "timestamp": report.timestamp,
            "summary": {
                "total_checks": report.total_checks,
                "passed": report.passed,
                "warnings": report.warnings,
                "failed": report.failed
            }
        }
