"""
LernsystemX Setup - Diagnostics (Part 2: Extended Checks & Reporting)

Extended diagnostic checks and report aggregation.

Provides:
- Extended component checks (Monitoring, Security, Storage, Celery)
- Aggregated diagnostics report (run_all_diagnostics)
- Report serialization (get_report_dict)

Phase 23 - Setup Wizard Erweiterungen
"""

from typing import List, Dict, Any
from dataclasses import asdict
from datetime import datetime
import os

from app.setup.diagnostics.checks.checks import (
    DiagnosticCheckResult,
    DiagnosticsReport,
    SystemDiagnosticsBase,
)


class SystemDiagnostics(SystemDiagnosticsBase):
    """
    Full system diagnostics runner for LernsystemX.

    Inherits core checks from SystemDiagnosticsBase and adds:
    - Monitoring, Security, Storage, Celery checks
    - Aggregated report generation
    - Report serialization
    """

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
            from app.core.bootstrap.extensions import redis_client

            # Check if Redis client is available
            if redis_client is None:
                return DiagnosticCheckResult(
                    name="Celery Configuration",
                    status="warn",
                    message="Celery broker not accessible (Redis not initialized)",
                    details={
                        "broker_configured": True,
                        "broker_accessible": False,
                        "error": "redis_client is None"
                    }
                )

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
