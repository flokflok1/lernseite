"""
LernsystemX Setup - Diagnostics (Part 1: Core Checks)

System diagnostics for health checks, configuration validation, and component status.

Provides:
- Data models (DiagnosticCheckResult, DiagnosticsReport)
- Core infrastructure checks (DB, Redis, AI Keys, Email, Backup)

See checks_part2.py for extended checks and report aggregation.

Phase 23 - Setup Wizard Erweiterungen
"""

from typing import Literal, Optional, List, Dict, Any
from dataclasses import dataclass
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


class SystemDiagnosticsBase:
    """
    Base system diagnostics for LernsystemX.

    Contains core infrastructure checks: Database, Redis, AI Keys, Email, Backup.
    Extended checks and report aggregation are in SystemDiagnostics (checks_part2.py).
    """

    @staticmethod
    def check_database_connection() -> DiagnosticCheckResult:
        """
        Check PostgreSQL database connectivity and configuration.

        Returns:
            DiagnosticCheckResult with connection status
        """
        try:
            from app.core.bootstrap import extensions

            if db_pool is None:
                return DiagnosticCheckResult(
                    name="Database Connection",
                    status="fail",
                    message="Database pool not initialized",
                    details={"error": "db_pool is None"},
                    auto_fix_available=False
                )

            # Test connection
            with extensions.db_pool.connection() as conn:
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
            from app.core.bootstrap.extensions import redis_client

            if redis_client is None:
                return DiagnosticCheckResult(
                    name="Redis Connection",
                    status="warn",
                    message="Redis client not initialized (normal during setup)",
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
                status="warn",
                message=f"Redis not available (normal during setup): {str(e)}",
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
