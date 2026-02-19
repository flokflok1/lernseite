"""
LernsystemX Setup - Infrastructure Verification Checks

Contains infrastructure verification check methods for:
- File system permissions
- Python dependency validation
- Environment variable verification
- Installation marker checks

Split from verify.py to satisfy the 500-line Quality Gate (G01).
These checks are inherited by VerificationChecks in verify.py.

ISO 9001:2015 compliant - Installation quality assurance
"""

from typing import Dict
import os


class InfrastructureVerificationChecks:
    """
    Infrastructure verification check methods.

    Contains checks for file system, dependencies, environment,
    and installation markers. Inherited by VerificationChecks.
    """

    REQUIRED_DIRECTORIES = [
        'uploads',
        'uploads/courses',
        'uploads/profiles',
        'logs',
        'cache',
        'temp'
    ]

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
