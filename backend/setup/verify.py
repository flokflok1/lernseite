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

    # Tables with schema prefixes (schema.table format)
    REQUIRED_TABLES = [
        ('core', 'users'),
        ('core', 'roles'),
        ('core', 'permissions'),
        ('organisations', 'organisations'),
        ('courses', 'courses'),
        ('courses', 'chapters'),
        ('courses', 'lessons'),
        ('courses', 'course_categories'),
        ('learning_methods', 'learning_method_types'),
        ('learning_methods', 'learning_method_instances'),
        ('billing_storage', 'token_wallets'),
        ('billing_storage', 'subscriptions'),
        ('core', 'audit_logs'),
        ('core', 'migration_history'),
        ('support_systems', 'system_features')
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
        """Check all required tables exist in their respective schemas"""
        try:
            # Get all tables from all schemas
            existing_tables = fetch_all(
                """
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                AND table_type = 'BASE TABLE'
                """
            )

            existing_table_set = {(row['table_schema'], row['table_name']) for row in existing_tables}
            missing_tables = []

            for schema, table in cls.REQUIRED_TABLES:
                if (schema, table) not in existing_table_set:
                    missing_tables.append(f'{schema}.{table}')

            if missing_tables:
                return {
                    'passed': False,
                    'message': f'Missing tables: {", ".join(missing_tables)}',
                    'details': {
                        'missing': missing_tables,
                        'existing': len(existing_table_set),
                        'required': len(cls.REQUIRED_TABLES)
                    }
                }

            return {
                'passed': True,
                'message': f'All {len(cls.REQUIRED_TABLES)} required tables exist',
                'details': {
                    'table_count': len(existing_table_set),
                    'schemas': list(set(row['table_schema'] for row in existing_tables if row['table_schema'] not in ('pg_catalog', 'information_schema')))
                }
            }

        except Exception as e:
            return {
                'passed': False,
                'message': f'Table check failed: {str(e)}'
            }

    @staticmethod
    def _check_database_indexes() -> Dict:
        """Check database indexes exist across all schemas"""
        try:
            indexes = fetch_all(
                """
                SELECT schemaname, tablename, indexname
                FROM pg_indexes
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
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
        """Check learning methods are seeded (12 Content-LMs expected)"""
        try:
            count = fetch_one("SELECT COUNT(*) FROM learning_methods.learning_method_types")
            method_count = count['count'] if count else 0

            # We expect exactly 12 Content-Lernmethoden (LM00-LM11)
            EXPECTED_LM_COUNT = 12

            if method_count == 0:
                return {
                    'passed': False,
                    'message': 'No learning methods found in database'
                }

            if method_count < EXPECTED_LM_COUNT:
                return {
                    'passed': True,
                    'message': f'{method_count} learning methods found (expected {EXPECTED_LM_COUNT})',
                    'warnings': ['Not all learning methods may be seeded'],
                    'details': {'count': method_count, 'expected': EXPECTED_LM_COUNT}
                }

            # Check group distribution (A, B, C)
            groups = fetch_all(
                """
                SELECT group_code, COUNT(*) as count
                FROM learning_methods.learning_method_types
                GROUP BY group_code
                """
            )

            group_counts = {row['group_code']: row['count'] for row in groups}

            return {
                'passed': True,
                'message': f'{method_count} learning methods seeded successfully',
                'details': {
                    'total': method_count,
                    'by_group': group_counts
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
            count = fetch_one("SELECT COUNT(*) FROM core.roles")
            role_count = count['count'] if count else 0

            if role_count == 0:
                return {
                    'passed': False,
                    'message': 'No roles found in database'
                }

            # Check critical roles exist
            critical_roles = ['free', 'premium', 'admin']
            existing_roles = fetch_all("SELECT role_name FROM core.roles WHERE role_name = ANY(%s)", (critical_roles,))
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
            count = fetch_one("SELECT COUNT(*) FROM courses.course_categories")
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
                FROM core.users u
                JOIN core.roles r ON u.role_id = r.role_id
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
                "SELECT organization_id, name, type, domain FROM organisations.organisations WHERE type IN ('system', 'academy')",
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
            for schema, table in cls.REQUIRED_TABLES:
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
