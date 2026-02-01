"""
LernsystemX Setup - System Status

Comprehensive system status reporting combining:
- Installation status
- Runtime status
- Version information
- Health indicators
- Migration status

Phase 23 - Setup Wizard Erweiterungen
"""

from typing import Dict, Any, Optional
from datetime import datetime
from flask import current_app


class SystemStatus:
    """
    Provides comprehensive system status information.

    Combines installation status, runtime health, versions, and migration state.
    """

    @staticmethod
    def get_installation_status() -> Dict[str, Any]:
        """
        Get installation status information.

        Returns:
            Dictionary with installation details
        """
        from setup.install_check import InstallationChecker

        is_installed = InstallationChecker.is_installed()
        install_info = InstallationChecker.get_install_info() if is_installed else None

        return {
            "installed": is_installed,
            "installation_completed_at": install_info.get('completed_at') if install_info else None,
            "installed_by": install_info.get('installed_by') if install_info else None,
            "install_version": install_info.get('version') if install_info else None
        }

    @staticmethod
    def get_version_information() -> Dict[str, Any]:
        """
        Get system version information.

        Returns:
            Dictionary with version details
        """
        from app.api.gateway.versioning import get_version_info

        try:
            version_info = get_version_info()
            return {
                "system_version": version_info.get('system_version', '1.0.0'),
                "environment": version_info.get('environment', 'production'),
                "api_version_current": version_info.get('api', {}).get('current_version', 1),
                "api_versions_supported": version_info.get('api', {}).get('supported_versions', [1])
            }
        except Exception:
            # Fallback if versioning not available
            return {
                "system_version": current_app.config.get('LSX_VERSION', '1.0.0'),
                "environment": current_app.config.get('LSX_ENV', 'production'),
                "api_version_current": current_app.config.get('API_VERSION_CURRENT', 1),
                "api_versions_supported": current_app.config.get('API_VERSION_SUPPORTED', '1').split(',')
            }

    @staticmethod
    def get_database_schema_version() -> Dict[str, Any]:
        """
        Get database schema version from migration history.

        Returns:
            Dictionary with DB schema version info
        """
        try:
            from app.core.bootstrap import extensions

            with extensions.db_pool.connection() as conn:
                with conn.cursor() as cur:
                    # Check if migration_history table exists
                    cur.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables
                            WHERE table_name = 'migration_history'
                        );
                    """)
                    has_migration_table = cur.fetchone()[0]

                    if not has_migration_table:
                        return {
                            "schema_version": "V001",  # Initial schema
                            "last_migration": None,
                            "last_migration_at": None,
                            "has_migration_table": False
                        }

                    # Get last migration
                    cur.execute("""
                        SELECT migration_name, version, executed_at
                        FROM migration_history
                        ORDER BY executed_at DESC
                        LIMIT 1;
                    """)
                    row = cur.fetchone()

                    if row:
                        return {
                            "schema_version": row[1],  # version
                            "last_migration": row[0],  # migration_name
                            "last_migration_at": row[2].isoformat() if row[2] else None,
                            "has_migration_table": True
                        }
                    else:
                        return {
                            "schema_version": "V001",
                            "last_migration": None,
                            "last_migration_at": None,
                            "has_migration_table": True
                        }

        except Exception as e:
            current_app.logger.error(f"Failed to get DB schema version: {str(e)}")
            return {
                "schema_version": "unknown",
                "last_migration": None,
                "last_migration_at": None,
                "error": str(e)
            }

    @staticmethod
    def get_migration_status() -> Dict[str, Any]:
        """
        Get migration status (pending migrations, etc.).

        Returns:
            Dictionary with migration status
        """
        try:
            from setup.migrations import MigrationManager

            migrations = MigrationManager.list_migrations()
            pending = [m for m in migrations if not m.get('applied', False)]

            return {
                "has_pending_migrations": len(pending) > 0,
                "pending_count": len(pending),
                "total_migrations": len(migrations),
                "applied_count": len(migrations) - len(pending)
            }

        except Exception as e:
            current_app.logger.error(f"Failed to get migration status: {str(e)}")
            return {
                "has_pending_migrations": False,
                "pending_count": 0,
                "total_migrations": 0,
                "applied_count": 0,
                "error": str(e)
            }

    @staticmethod
    def get_health_status() -> Dict[str, Any]:
        """
        Get overall health status from diagnostics.

        Returns:
            Dictionary with health information
        """
        from setup.diagnostics import SystemDiagnostics

        # Run quick diagnostics (core checks only)
        report = SystemDiagnostics.run_all_diagnostics(quick=True)

        return {
            "overall_health": report.overall_status,
            "checks_passed": report.passed,
            "checks_warned": report.warnings,
            "checks_failed": report.failed,
            "total_checks": report.total_checks,
            "last_check_at": report.timestamp
        }

    @staticmethod
    def get_component_status() -> Dict[str, str]:
        """
        Get individual component status (ok/warn/fail).

        Returns:
            Dictionary mapping component names to status
        """
        from setup.diagnostics import SystemDiagnostics

        components = {
            "database": SystemDiagnostics.check_database_connection(),
            "redis": SystemDiagnostics.check_redis_connection(),
            "security": SystemDiagnostics.check_security_config()
        }

        return {
            name: check.status
            for name, check in components.items()
        }

    @staticmethod
    def get_system_status() -> Dict[str, Any]:
        """
        Get comprehensive system status.

        Combines all status information into a single report.

        Returns:
            Dictionary with complete system status
        """
        # Get all status components
        installation = SystemStatus.get_installation_status()
        versions = SystemStatus.get_version_information()
        db_schema = SystemStatus.get_database_schema_version()
        migrations = SystemStatus.get_migration_status()
        health = SystemStatus.get_health_status()
        components = SystemStatus.get_component_status()

        # Build comprehensive status
        status = {
            # Installation info
            "installed": installation["installed"],
            "installation_completed_at": installation["installation_completed_at"],

            # Environment & versions
            "environment": versions["environment"],
            "system_version": versions["system_version"],
            "api_version": versions["api_version_current"],
            "api_versions_supported": versions["api_versions_supported"],

            # Database schema
            "db_schema_version": db_schema["schema_version"],
            "last_migration": db_schema["last_migration"],
            "last_migration_at": db_schema["last_migration_at"],

            # Migrations
            "has_pending_migrations": migrations["has_pending_migrations"],
            "pending_migrations_count": migrations["pending_count"],

            # Health
            "overall_health": health["overall_health"],
            "health_summary": {
                "passed": health["checks_passed"],
                "warnings": health["checks_warned"],
                "failed": health["checks_failed"]
            },

            # Components
            "components": components,

            # Metadata
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }

        # Add optional fields
        if installation["installed_by"]:
            status["installed_by"] = installation["installed_by"]

        if db_schema.get("error"):
            status["db_schema_error"] = db_schema["error"]

        if migrations.get("error"):
            status["migrations_error"] = migrations["error"]

        return status

    @staticmethod
    def get_status_summary() -> Dict[str, Any]:
        """
        Get lightweight status summary (for quick checks).

        Returns:
            Dictionary with essential status info
        """
        installation = SystemStatus.get_installation_status()
        versions = SystemStatus.get_version_information()
        migrations = SystemStatus.get_migration_status()

        return {
            "installed": installation["installed"],
            "system_version": versions["system_version"],
            "environment": versions["environment"],
            "has_pending_migrations": migrations["has_pending_migrations"],
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
