"""
LernsystemX Setup - System Requirements Check

Performs comprehensive system checks before installation:
- Python version (3.12+)
- PostgreSQL connection
- Redis connection
- Filesystem permissions
- Port availability
- Required dependencies

Based on ISO 9001:2015 Quality Management - Prevention approach
"""

import sys
import os
import socket
from typing import Dict, List, Tuple

import psycopg


class SystemCheck:
    """
    Performs comprehensive system checks before setup

    All checks must pass before proceeding with installation.
    Implements fail-fast principle for early error detection.
    """

    REQUIRED_PYTHON = (3, 12)
    REQUIRED_PORTS = [5000, 5432, 6379]  # Flask, PostgreSQL, Redis
    REQUIRED_DIRS = ['uploads', 'logs', 'cache']

    @staticmethod
    def check_all() -> Tuple[bool, List[Dict]]:
        """
        Run all system checks

        Returns:
            Tuple[bool, List[Dict]]: (all_passed, results_list)

        Example:
            >>> all_passed, results = SystemCheck.check_all()
            >>> if all_passed:
            ...     print("System ready for installation")
        """
        results = []

        # 1. Python Version
        results.append(SystemCheck._check_python())

        # 2. PostgreSQL Connection
        results.append(SystemCheck._check_postgres())

        # 3. Redis Connection
        results.append(SystemCheck._check_redis())

        # 4. Filesystem Permissions
        results.append(SystemCheck._check_filesystem())

        # 5. Port Availability
        results.append(SystemCheck._check_ports())

        # 6. Dependencies
        results.append(SystemCheck._check_dependencies())

        # Check if all passed
        all_passed = all(r['status'] == 'ok' for r in results)

        return all_passed, results

    @staticmethod
    def _check_python() -> Dict:
        """Check Python version meets requirements"""
        current = sys.version_info[:2]
        required = SystemCheck.REQUIRED_PYTHON

        if current >= required:
            return {
                'name': 'Python Version',
                'status': 'ok',
                'message': f'Python {current[0]}.{current[1]} installed',
                'details': sys.version.split()[0]
            }
        else:
            return {
                'name': 'Python Version',
                'status': 'error',
                'message': f'Python {required[0]}.{required[1]}+ required',
                'details': f'Current: {current[0]}.{current[1]}'
            }

    @staticmethod
    def _check_postgres() -> Dict:
        """Check PostgreSQL connection and version"""
        try:
            # Attempt connection with environment variables
            conn = psycopg.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', 5432)),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', ''),
                dbname=os.getenv('DB_NAME', 'postgres')  # Connect to default DB first
            )

            # Get PostgreSQL version
            cursor = conn.cursor()
            cursor.execute('SELECT version();')
            version = cursor.fetchone()[0]

            # Extract version number
            version_short = version.split()[1]

            cursor.close()
            conn.close()

            return {
                'name': 'PostgreSQL',
                'status': 'ok',
                'message': 'PostgreSQL connected',
                'details': f'Version: {version_short}'
            }

        except psycopg.OperationalError as e:
            return {
                'name': 'PostgreSQL',
                'status': 'error',
                'message': 'Cannot connect to PostgreSQL',
                'details': str(e)
            }
        except Exception as e:
            return {
                'name': 'PostgreSQL',
                'status': 'error',
                'message': 'PostgreSQL check failed',
                'details': str(e)
            }

    @staticmethod
    def _check_redis() -> Dict:
        """Check Redis connection and version"""
        try:
            import redis

            r = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=0,
                decode_responses=True,
                socket_connect_timeout=5
            )

            # Test connection
            r.ping()

            # Get Redis version
            info = r.info('server')
            redis_version = info.get('redis_version', 'unknown')

            return {
                'name': 'Redis',
                'status': 'ok',
                'message': 'Redis connected',
                'details': f'Version: {redis_version}'
            }

        except redis.ConnectionError as e:
            return {
                'name': 'Redis',
                'status': 'error',
                'message': 'Cannot connect to Redis',
                'details': 'Make sure Redis server is running'
            }
        except ImportError:
            return {
                'name': 'Redis',
                'status': 'error',
                'message': 'Redis client not installed',
                'details': 'Run: pip install redis'
            }
        except Exception as e:
            return {
                'name': 'Redis',
                'status': 'error',
                'message': 'Redis check failed',
                'details': str(e)
            }

    @staticmethod
    def _check_filesystem() -> Dict:
        """Check filesystem permissions for required directories"""
        errors = []

        for dir_name in SystemCheck.REQUIRED_DIRS:
            path = os.path.join(os.getcwd(), 'backend', dir_name)

            # Try to create directory
            try:
                os.makedirs(path, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create {dir_name}: {str(e)}")
                continue

            # Test write permission
            test_file = os.path.join(path, '.test_write')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except Exception as e:
                errors.append(f"No write permission in {dir_name}: {str(e)}")

        if errors:
            return {
                'name': 'Filesystem',
                'status': 'error',
                'message': 'Filesystem permission errors',
                'details': '; '.join(errors)
            }
        else:
            return {
                'name': 'Filesystem',
                'status': 'ok',
                'message': 'All directories writable',
                'details': f"Checked: {', '.join(SystemCheck.REQUIRED_DIRS)}"
            }

    @staticmethod
    def _check_ports() -> Dict:
        """Check if required ports are available"""
        occupied = []

        for port in SystemCheck.REQUIRED_PORTS:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()

            # Port is occupied if connection succeeds (result == 0)
            # Exception: PostgreSQL (5432) and Redis (6379) should be running
            if result == 0:
                if port == 5000:  # Flask port must be free
                    occupied.append(port)
                # 5432 and 6379 being occupied is expected (they should be running)

        if occupied:
            return {
                'name': 'Ports',
                'status': 'error',
                'message': 'Required ports occupied',
                'details': f"Port(s) in use: {', '.join(map(str, occupied))}"
            }
        else:
            return {
                'name': 'Ports',
                'status': 'ok',
                'message': 'Application port available',
                'details': 'Port 5000 is free'
            }

    @staticmethod
    def _check_dependencies() -> Dict:
        """Check if critical Python packages are installed"""
        required_packages = [
            'flask',
            'sqlalchemy',
            'psycopg',
            'redis',
            'celery',
            'jwt',
            'bcrypt',
            'marshmallow'
        ]

        missing = []

        for package in required_packages:
            try:
                # Handle package name variations
                import_name = package
                if package == 'jwt':
                    import_name = 'jwt'
                elif package == 'psycopg':
                    import_name = 'psycopg'

                __import__(import_name)
            except ImportError:
                missing.append(package)

        if missing:
            return {
                'name': 'Dependencies',
                'status': 'warning',
                'message': 'Some packages missing',
                'details': f"Missing: {', '.join(missing)}"
            }
        else:
            return {
                'name': 'Dependencies',
                'status': 'ok',
                'message': 'All dependencies installed',
                'details': f'{len(required_packages)} packages checked'
            }


# Convenience function for quick checks
def is_system_ready() -> bool:
    """
    Quick check if system is ready for installation

    Returns:
        bool: True if all checks pass, False otherwise
    """
    all_passed, _ = SystemCheck.check_all()
    return all_passed
