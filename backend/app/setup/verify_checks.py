"""
LernsystemX Setup - Verification Check Methods

Contains all individual verification check methods for:
- Database schema validation
- Seed data verification
- System configuration validation
- Infrastructure checks (files, dependencies, environment)

This module is imported by verify.py for verification orchestration.

ISO 9001:2015 compliant - Installation quality assurance
"""

from typing import Dict, List, Tuple
import os
import sys

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query


class VerificationChecks:
    """
    Verification check methods.

    Contains all individual verification checks.
    Called by SetupVerification.verify_all() orchestrator.
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

    @staticmethod
    def check_database_connection() -> Dict:
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
    def check_database_tables(cls) -> Dict:
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
    def check_database_indexes() -> Dict:
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
    def check_learning_methods() -> Dict:
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
    def check_roles() -> Dict:
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
    def check_categories() -> Dict:
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
    def check_admin_account() -> Dict:
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
    def check_organisation() -> Dict:
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
    def check_file_permissions(cls) -> Dict:
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
    def check_dependencies() -> Dict:
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
    def check_environment() -> Dict:
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
    def check_installation_marker() -> Dict:
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
