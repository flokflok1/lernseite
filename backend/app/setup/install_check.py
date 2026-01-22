"""
LernsystemX Setup - Installation Status Check

Checks if the system has been installed and configured.
Creates and validates .lsx-installed marker file.

ISO 9001:2015 compliant - Installation verification
"""

import os
import json
from typing import Dict, Optional
from datetime import datetime


class InstallationChecker:
    """
    Check and manage installation status

    Uses .lsx-installed file as marker for completed installation.
    File contains metadata about the installation.
    """

    INSTALL_MARKER_FILE = '.lsx-installed'

    @staticmethod
    def is_installed() -> bool:
        """
        Check if system is installed

        Returns:
            bool: True if installation completed, False otherwise

        Example:
            >>> if InstallationChecker.is_installed():
            ...     print("System already installed")
            ... else:
            ...     print("Run setup wizard")
        """
        return os.path.exists(InstallationChecker.INSTALL_MARKER_FILE)

    @staticmethod
    def get_install_info() -> Optional[Dict]:
        """
        Get installation information

        Returns:
            Dict or None: Installation metadata if exists

        Example:
            >>> info = InstallationChecker.get_install_info()
            >>> if info:
            ...     print(f"Installed on: {info['installed_at']}")
            ...     print(f"Version: {info['version']}")
        """
        if not InstallationChecker.is_installed():
            return None

        try:
            with open(InstallationChecker.INSTALL_MARKER_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading install info: {e}")
            return None

    @staticmethod
    def mark_as_installed(
        version: str = '1.0.0',
        database_version: str = '1.0.0',
        admin_email: Optional[str] = None,
        extra_info: Optional[Dict] = None
    ) -> bool:
        """
        Mark system as installed

        Args:
            version: Application version
            database_version: Database schema version
            admin_email: Admin user email (optional)
            extra_info: Additional metadata (optional)

        Returns:
            bool: True if marker created successfully

        Example:
            >>> InstallationChecker.mark_as_installed(
            ...     version='1.0.0',
            ...     admin_email='admin@example.com'
            ... )
        """
        try:
            install_info = {
                'installed': True,
                'installed_at': datetime.utcnow().isoformat(),
                'version': version,
                'database_version': database_version,
                'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
                'admin_email': admin_email
            }

            # Add extra info if provided
            if extra_info:
                install_info.update(extra_info)

            # Write marker file (backend)
            with open(InstallationChecker.INSTALL_MARKER_FILE, 'w') as f:
                json.dump(install_info, f, indent=2)

            # ALSO write marker to frontend/public/ for offline detection
            # This allows frontend to detect installation even when backend is down
            frontend_marker_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'frontend', 'public', '.lsx-installed'
            )

            try:
                os.makedirs(os.path.dirname(frontend_marker_path), exist_ok=True)
                with open(frontend_marker_path, 'w') as f:
                    # Write minimal info to frontend marker (no sensitive data)
                    frontend_info = {
                        'installed': True,
                        'version': version,
                        'installed_at': install_info['installed_at']
                    }
                    json.dump(frontend_info, f, indent=2)
                print(f"[Install Check] Frontend marker created at {frontend_marker_path}")
            except Exception as fe:
                print(f"[Install Check] Warning: Could not create frontend marker: {fe}")
                # Don't fail if frontend marker fails - backend marker is source of truth

            return True

        except Exception as e:
            print(f"Error creating install marker: {e}")
            return False

    @staticmethod
    def remove_install_marker() -> bool:
        """
        Remove installation marker (for testing/reinstall)

        Returns:
            bool: True if removed successfully

        Warning:
            This will allow setup wizard to run again.
            Use with caution - may cause data loss!
        """
        try:
            removed = False

            # Remove backend marker
            if os.path.exists(InstallationChecker.INSTALL_MARKER_FILE):
                os.remove(InstallationChecker.INSTALL_MARKER_FILE)
                removed = True

            # Remove frontend marker
            frontend_marker_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'frontend', 'public', '.lsx-installed'
            )
            if os.path.exists(frontend_marker_path):
                os.remove(frontend_marker_path)
                print(f"[Install Check] Frontend marker removed")
                removed = True

            return removed

        except Exception as e:
            print(f"Error removing install marker: {e}")
            return False

    @staticmethod
    def verify_installation() -> Dict:
        """
        Verify installation is complete and valid

        Returns:
            Dict with verification results:
            - installed: bool
            - valid: bool
            - version: str
            - checks: Dict of verification checks

        Example:
            >>> result = InstallationChecker.verify_installation()
            >>> if result['valid']:
            ...     print("Installation valid")
        """
        result = {
            'installed': False,
            'valid': False,
            'version': None,
            'checks': {}
        }

        # Check if installed
        if not InstallationChecker.is_installed():
            result['checks']['marker_file'] = {
                'status': 'error',
                'message': 'Installation marker not found'
            }
            return result

        result['installed'] = True

        # Get install info
        install_info = InstallationChecker.get_install_info()

        if not install_info:
            result['checks']['install_info'] = {
                'status': 'error',
                'message': 'Cannot read installation info'
            }
            return result

        result['version'] = install_info.get('version')

        # Check database connection
        try:
            from setup.db_init import DatabaseInitializer
            db_init = DatabaseInitializer()
            db_init.engine = db_init._create_engine()

            # Quick connection test
            with db_init.engine.connect() as conn:
                conn.execute("SELECT 1")

            result['checks']['database'] = {
                'status': 'ok',
                'message': 'Database accessible'
            }

        except Exception as e:
            result['checks']['database'] = {
                'status': 'error',
                'message': f'Database connection failed: {str(e)}'
            }
            return result

        # Check if admin user exists
        try:
            from sqlalchemy import text
            with db_init.engine.connect() as conn:
                admin_check = conn.execute(
                    text("SELECT COUNT(*) FROM users WHERE role = 'superadmin'")
                )
                admin_count = admin_check.scalar()

                if admin_count > 0:
                    result['checks']['admin'] = {
                        'status': 'ok',
                        'message': 'Admin user exists'
                    }
                else:
                    result['checks']['admin'] = {
                        'status': 'warning',
                        'message': 'No admin user found'
                    }

        except Exception as e:
            result['checks']['admin'] = {
                'status': 'error',
                'message': f'Cannot verify admin user: {str(e)}'
            }

        # All checks passed?
        result['valid'] = all(
            check.get('status') in ['ok', 'warning']
            for check in result['checks'].values()
        )

        return result


# Convenience functions
def is_installed() -> bool:
    """Quick check if installed"""
    return InstallationChecker.is_installed()


def require_setup() -> bool:
    """
    Check if setup is required

    Returns:
        bool: True if setup wizard should run
    """
    return not InstallationChecker.is_installed()


def mark_installed(**kwargs) -> bool:
    """Quick mark as installed"""
    return InstallationChecker.mark_as_installed(**kwargs)
