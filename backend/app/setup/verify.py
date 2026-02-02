"""
LernsystemX Setup - Post-Installation Verification (Orchestration & Reporting)

Comprehensive verification of installation:
- Database schema validation
- Seed data verification
- Admin account check
- Organisation setup verification
- System configuration validation
- File permissions check
- Dependency verification

Individual check methods are defined in:
- app.setup.verify_checks - VerificationChecks class with all check methods

ISO 9001:2015 compliant - Installation quality assurance
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime
import os
import sys

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query
from app.setup.verify_checks import VerificationChecks


class SetupVerification:
    """
    Post-installation verification orchestration and reporting.

    Orchestrates verification checks from VerificationChecks class.
    Provides result aggregation, reporting, and system info gathering.
    """

    @classmethod
    def verify_all(cls) -> Dict:
        """
        Run all verification checks.

        Orchestrates verification checks from VerificationChecks class.
        Aggregates results and returns comprehensive verification report.

        Returns:
            Dictionary with verification results:
            - success: bool - Overall verification status
            - checks: List[Dict] - Individual check results
            - errors: List[str] - Error messages
            - warnings: List[str] - Warning messages
            - timestamp: str - ISO timestamp of verification

        Example:
            >>> results = SetupVerification.verify_all()
            >>> if results['success']:
            ...     print("Installation verified successfully!")
            ... else:
            ...     print(f"Verification failed: {results['errors']}")
        """
        results = {
            'success': True,
            'checks': [],
            'errors': [],
            'warnings': [],
            'timestamp': datetime.utcnow().isoformat()
        }

        # Run all verification checks from VerificationChecks
        checks = [
            ('Database Connection', VerificationChecks.check_database_connection),
            ('Database Tables', VerificationChecks.check_database_tables),
            ('Database Indexes', VerificationChecks.check_database_indexes),
            ('Seed Data - Learning Methods', VerificationChecks.check_learning_methods),
            ('Seed Data - Groups', VerificationChecks.check_groups),
            ('Seed Data - Categories', VerificationChecks.check_categories),
            ('Admin Account', VerificationChecks.check_admin_account),
            ('Organisation Setup', VerificationChecks.check_organisation),
            ('File Permissions', VerificationChecks.check_file_permissions),
            ('Python Dependencies', VerificationChecks.check_dependencies),
            ('Environment Variables', VerificationChecks.check_environment)
            # Note: Installation Marker check removed - marker should only exist AFTER setup completes
            # Note: Roles check replaced with Groups check (PHASE B: Groups replace Roles)
        ]

        for check_name, check_func in checks:
            try:
                check_result = check_func()
                results['checks'].append({
                    'name': check_name,
                    'status': 'passed' if check_result['passed'] else 'failed',
                    'message': check_result.get('message', ''),
                    'details': check_result.get('details', {})
                })

                if not check_result['passed']:
                    results['success'] = False
                    results['errors'].append(f"{check_name}: {check_result.get('message', 'Check failed')}")

                if check_result.get('warnings'):
                    results['warnings'].extend(check_result['warnings'])

            except Exception as e:
                results['success'] = False
                results['errors'].append(f"{check_name}: {str(e)}")
                results['checks'].append({
                    'name': check_name,
                    'status': 'error',
                    'message': str(e)
                })

        return results

    @classmethod
    def generate_report(cls) -> str:
        """
        Generate verification report

        Returns:
            Formatted verification report

        Example:
            >>> report = SetupVerification.generate_report()
            >>> print(report)
        """
        results = cls.verify_all()

        report_lines = [
            "=" * 70,
            "LernsystemX Installation Verification Report",
            "=" * 70,
            f"Timestamp: {results['timestamp']}",
            f"Overall Status: {'PASSED' if results['success'] else 'FAILED'}",
            "",
            "Verification Checks:",
            "-" * 70
        ]

        for check in results['checks']:
            status_symbol = "✓" if check['status'] == 'passed' else "✗"
            report_lines.append(f"{status_symbol} {check['name']}: {check['status'].upper()}")
            if check.get('message'):
                report_lines.append(f"  → {check['message']}")

        if results['warnings']:
            report_lines.extend([
                "",
                "Warnings:",
                "-" * 70
            ])
            for warning in results['warnings']:
                report_lines.append(f"⚠ {warning}")

        if results['errors']:
            report_lines.extend([
                "",
                "Errors:",
                "-" * 70
            ])
            for error in results['errors']:
                report_lines.append(f"✗ {error}")

        report_lines.extend([
            "",
            "=" * 70,
            f"Summary: {len([c for c in results['checks'] if c['status'] == 'passed'])}/{len(results['checks'])} checks passed",
            "=" * 70
        ])

        return "\n".join(report_lines)

    @classmethod
    def get_system_info(cls) -> Dict:
        """
        Get system information

        Returns:
            Dictionary with system info

        Example:
            >>> info = SetupVerification.get_system_info()
        """
        try:
            import platform

            # Get database info
            db_version = fetch_one("SELECT version()")

            # Get table counts
            table_counts = {}
            for schema, table in VerificationChecks.REQUIRED_TABLES:
                full_name = f"{schema}.{table}"
                try:
                    count = fetch_one(f"SELECT COUNT(*) FROM {full_name}")
                    table_counts[full_name] = count['count'] if count else 0
                except:
                    table_counts[full_name] = 'Error'

            return {
                'python_version': sys.version,
                'platform': platform.platform(),
                'database_version': db_version.get('version', 'Unknown') if db_version else 'Unknown',
                'table_counts': table_counts,
                'environment': os.getenv('FLASK_ENV', 'unknown')
            }

        except Exception as e:
            return {
                'error': str(e)
            }


# Convenience functions
def verify_all() -> Dict:
    """Quick function to run all verification checks"""
    return SetupVerification.verify_all()


def generate_report() -> str:
    """Quick function to generate verification report"""
    return SetupVerification.generate_report()


def get_system_info() -> Dict:
    """Quick function to get system info"""
    return SetupVerification.get_system_info()
