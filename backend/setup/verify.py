"""
LernsystemX Setup - Post-Installation Verification

Comprehensive verification of installation:
- Database schema validation
- Seed data verification
- Admin account check
- Organisation setup verification
- System configuration validation
- File permissions check
- Dependency verification

ISO 9001:2015 compliant - Installation quality assurance
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime
import os
import sys

from app.database.connection import fetch_one, fetch_all, execute_query


class SetupVerification:
    """
    Post-installation verification

    Validates that all setup steps completed successfully.
    """

    REQUIRED_TABLES = [
        'users',
        'roles',
        'organizations',
        'courses',
        'modules',
        'learning_method_types',
        'token_wallets',
        'token_transactions',
        'subscriptions',
        'audit_logs',
        'migration_history',
        'course_categories',
        'recovery_codes'
    ]

    REQUIRED_DIRECTORIES = [
        'uploads',
        'uploads/courses',
        'uploads/profiles',
        'logs',
        'cache',
        'temp'
    ]

    @classmethod
    def verify_all(cls) -> Dict:
        """
        Run all verification checks

        Returns:
            Dictionary with verification results

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

        # Run all verification checks
        checks = [
            ('Database Connection', cls._check_database_connection),
            ('Database Tables', cls._check_database_tables),
            ('Database Indexes', cls._check_database_indexes),
            ('Seed Data - Learning Methods', cls._check_learning_methods),
            ('Seed Data - Roles', cls._check_roles),
            ('Seed Data - Categories', cls._check_categories),
            ('Admin Account', cls._check_admin_account),
            ('Organisation Setup', cls._check_organisation),
            ('File Permissions', cls._check_file_permissions),
            ('Python Dependencies', cls._check_dependencies),
            ('Environment Variables', cls._check_environment)
            # Note: Installation Marker check removed - marker should only exist AFTER setup completes
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

    @staticmethod
    def _check_database_connection() -> Dict:
        """Check database connectivity"""
        try:
            result = fetch_one("SELECT version()")
            if result:
                return {
                    'passed': True,
                    'message': 'Database connection successful',
                    'details': {'version': result.get('version', 'Unknown')}
                }
            else:
                return {
                    'passed': False,
                    'message': 'Could not retrieve database version'
                }
        except Exception as e:
            return {
                'passed': False,
                'message': f'Database connection failed: {str(e)}'
            }

    @classmethod
    def _check_database_tables(cls) -> Dict:
        """Check all required tables exist"""
        try:
            existing_tables = fetch_all(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                """
            )

            existing_table_names = {row['table_name'] for row in existing_tables}
            missing_tables = set(cls.REQUIRED_TABLES) - existing_table_names

            if missing_tables:
                return {
                    'passed': False,
                    'message': f'Missing tables: {", ".join(missing_tables)}',
                    'details': {
                        'missing': list(missing_tables),
                        'existing': len(existing_table_names),
                        'required': len(cls.REQUIRED_TABLES)
                    }
                }

            return {
                'passed': True,
                'message': f'All {len(cls.REQUIRED_TABLES)} required tables exist',
                'details': {
                    'table_count': len(existing_table_names),
                    'tables': list(existing_table_names)
                }
            }

        except Exception as e:
            return {
                'passed': False,
                'message': f'Table check failed: {str(e)}'
            }

    @staticmethod
    def _check_database_indexes() -> Dict:
        """Check database indexes exist"""
        try:
            indexes = fetch_all(
                """
                SELECT schemaname, tablename, indexname
                FROM pg_indexes
                WHERE schemaname = 'public'
                """
            )

            if len(indexes) < 10:
                return {
                    'passed': False,
                    'message': f'Too few indexes found ({len(indexes)}), expected at least 10',
                    'warnings': ['Consider running database optimization']
                }

            return {
                'passed': True,
                'message': f'{len(indexes)} indexes found',
                'details': {'index_count': len(indexes)}
            }

        except Exception as e:
            return {
                'passed': False,
                'message': f'Index check failed: {str(e)}'
            }

    @staticmethod
    def _check_learning_methods() -> Dict:
        """Check learning methods are seeded"""
        try:
            count = fetch_one("SELECT COUNT(*) FROM learning_method_types")
            method_count = count['count'] if count else 0

            if method_count == 0:
                return {
                    'passed': False,
                    'message': 'No learning methods found in database'
                }

            if method_count < 21:
                return {
                    'passed': True,
                    'message': f'{method_count} learning methods found (expected 21)',
                    'warnings': ['Not all learning methods may be seeded'],
                    'details': {'count': method_count, 'expected': 21}
                }

            # Check tier distribution
            tiers = fetch_all(
                """
                SELECT tier, COUNT(*) as count
                FROM learning_method_types
                GROUP BY tier
                """
            )

            tier_counts = {row['tier']: row['count'] for row in tiers}

            return {
                'passed': True,
                'message': f'{method_count} learning methods seeded successfully',
                'details': {
                    'total': method_count,
                    'by_tier': tier_counts
                }
            }

        except Exception as e:
            return {
                'passed': False,
                'message': f'Learning methods check failed: {str(e)}'
            }

    @staticmethod
    def _check_roles() -> Dict:
        """Check user roles are seeded"""
        try:
            count = fetch_one("SELECT COUNT(*) FROM roles")
            role_count = count['count'] if count else 0

            if role_count == 0:
                return {
                    'passed': False,
                    'message': 'No roles found in database'
                }

            # Check critical roles exist
            critical_roles = ['free', 'premium', 'admin']
            existing_roles = fetch_all("SELECT role_name FROM roles WHERE role_name = ANY(%s)", (critical_roles,))
            existing_role_names = {row['role_name'] for row in existing_roles}

            missing_critical = set(critical_roles) - existing_role_names

            if missing_critical:
                return {
                    'passed': False,
                    'message': f'Missing critical roles: {", ".join(missing_critical)}',
                    'details': {'missing': list(missing_critical)}
                }

            return {
                'passed': True,
                'message': f'{role_count} roles configured',
                'details': {'role_count': role_count}
            }

        except Exception as e:
            return {
                'passed': False,
                'message': f'Roles check failed: {str(e)}'
            }

    @staticmethod
    def _check_categories() -> Dict:
        """Check categories are seeded"""
        try:
            count = fetch_one("SELECT COUNT(*) FROM course_categories")
            category_count = count['count'] if count else 0

            if category_count == 0:
                return {
                    'passed': True,
                    'message': 'No categories found (optional)',
                    'warnings': ['Categories not seeded - consider adding them'],
                    'details': {'count': 0}
                }

            return {
                'passed': True,
                'message': f'{category_count} categories configured',
                'details': {'category_count': category_count}
            }

        except Exception as e:
            return {
                'passed': False,
                'message': f'Categories check failed: {str(e)}'
            }

    @staticmethod
    def _check_admin_account() -> Dict:
        """Check admin account exists"""
        try:
            admin = fetch_one(
                """
                SELECT u.user_id, u.email, u.firstname, u.lastname
                FROM users u
                JOIN roles r ON u.role_id = r.role_id
                WHERE r.role_name = %s
                """,
                ('admin',)
            )

            if not admin:
                return {
                    'passed': False,
                    'message': 'No admin account found'
                }

            return {
                'passed': True,
                'message': f'Admin account exists: {admin["email"]}',
                'details': {
                    'user_id': admin['user_id'],
                    'email': admin['email'],
                    'name': f"{admin['firstname']} {admin['lastname']}"
                }
            }

        except Exception as e:
            return {
                'passed': False,
                'message': f'Admin account check failed: {str(e)}'
            }

    @staticmethod
    def _check_organisation() -> Dict:
        """Check LSX Academy organisation exists"""
        try:
            org = fetch_one(
                "SELECT organization_id, name, type, domain FROM organizations WHERE type IN ('system', 'academy')",
                ()
            )

            if not org:
                return {
                    'passed': False,
                    'message': 'No system/academy organisation found'
                }

            return {
                'passed': True,
                'message': f'System organisation exists: {org["name"]}',
                'details': {
                    'organization_id': org['organization_id'],
                    'name': org['name'],
                    'domain': org.get('domain', 'N/A')
                }
            }

        except Exception as e:
            return {
                'passed': False,
                'message': f'Organisation check failed: {str(e)}'
            }

    @classmethod
    def _check_file_permissions(cls) -> Dict:
        """Check required directories exist and are writable"""
        missing_dirs = []
        unwritable_dirs = []

        for directory in cls.REQUIRED_DIRECTORIES:
            dir_path = os.path.join(os.getcwd(), directory)

            if not os.path.exists(dir_path):
                missing_dirs.append(directory)
            elif not os.access(dir_path, os.W_OK):
                unwritable_dirs.append(directory)

        if missing_dirs or unwritable_dirs:
            errors = []
            if missing_dirs:
                errors.append(f"Missing: {', '.join(missing_dirs)}")
            if unwritable_dirs:
                errors.append(f"Not writable: {', '.join(unwritable_dirs)}")

            return {
                'passed': False,
                'message': '; '.join(errors),
                'details': {
                    'missing': missing_dirs,
                    'unwritable': unwritable_dirs
                }
            }

        return {
            'passed': True,
            'message': f'All {len(cls.REQUIRED_DIRECTORIES)} required directories exist and are writable'
        }

    @staticmethod
    def _check_dependencies() -> Dict:
        """Check critical Python dependencies are installed"""
        critical_packages = [
            'flask',
            'psycopg',
            'bcrypt',
            'jwt',
            'redis',
            'celery',
            'cryptography'
        ]

        missing_packages = []

        for package in critical_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            return {
                'passed': False,
                'message': f'Missing packages: {", ".join(missing_packages)}',
                'details': {'missing': missing_packages}
            }

        return {
            'passed': True,
            'message': 'All critical dependencies installed',
            'details': {
                'checked': len(critical_packages),
                'packages': critical_packages
            }
        }

    @staticmethod
    def _check_environment() -> Dict:
        """Check critical environment variables"""
        critical_env_vars = [
            'DATABASE_URL',
            'SECRET_KEY',
            'FLASK_ENV'
        ]

        missing_vars = []
        empty_vars = []

        for var in critical_env_vars:
            value = os.getenv(var)
            if value is None:
                missing_vars.append(var)
            elif not value.strip():
                empty_vars.append(var)

        if missing_vars or empty_vars:
            errors = []
            if missing_vars:
                errors.append(f"Missing: {', '.join(missing_vars)}")
            if empty_vars:
                errors.append(f"Empty: {', '.join(empty_vars)}")

            return {
                'passed': False,
                'message': '; '.join(errors),
                'details': {
                    'missing': missing_vars,
                    'empty': empty_vars
                }
            }

        return {
            'passed': True,
            'message': 'All critical environment variables are set'
        }

    @staticmethod
    def _check_installation_marker() -> Dict:
        """Check .lsx-installed marker file exists"""
        marker_file = '.lsx-installed'

        if not os.path.exists(marker_file):
            return {
                'passed': False,
                'message': 'Installation marker file not found'
            }

        try:
            with open(marker_file, 'r') as f:
                content = f.read()

            return {
                'passed': True,
                'message': 'Installation marker file exists',
                'details': {'content': content[:100]}
            }

        except Exception as e:
            return {
                'passed': False,
                'message': f'Could not read installation marker: {str(e)}'
            }

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
            for table in cls.REQUIRED_TABLES:
                try:
                    count = fetch_one(f"SELECT COUNT(*) FROM {table}")
                    table_counts[table] = count['count'] if count else 0
                except:
                    table_counts[table] = 'Error'

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
