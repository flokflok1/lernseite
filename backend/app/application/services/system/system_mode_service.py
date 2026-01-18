"""
LernsystemX System Mode Service

Business logic for system environment and maintenance mode management.

Features:
- Environment switching (development/production)
- Maintenance mode toggle
- System status retrieval
- Mode validation
"""

from typing import Dict, Optional
from datetime import datetime
import os
import time

from app.infrastructure.persistence.repositories.settings.system import SystemSettingsRepository
from flask import current_app


class SystemModeService:
    """
    System Mode Service

    Manages system-wide environment settings and maintenance mode.
    """

    # Start time for uptime calculation
    _start_time = time.time()

    @classmethod
    def switch_environment(cls, environment: str, user_id: str = None) -> Dict:
        """
        Switch system environment (development/production)

        Args:
            environment: Target environment ('development' or 'production')
            user_id: User ID performing the switch (for audit)

        Returns:
            Dict with success status and message
        """
        current_env = cls.get_current_environment()

        # Validate switch
        if environment == current_env:
            return {
                'success': False,
                'error': f'System is already in {environment} mode',
                'current_environment': current_env
            }

        if environment not in ['development', 'production']:
            return {
                'success': False,
                'error': f'Invalid environment: {environment}'
            }

        # Update system setting
        success = SystemSettingsRepository.update_setting(
            'system.environment',
            environment,
            value_type='string'
        )

        if not success:
            # Setting doesn't exist, create it
            SystemSettingsRepository.create_setting(
                key='system.environment',
                value=environment,
                category='system',
                description='System environment mode (development/production)',
                editable=True,
                value_type='string'
            )

        # Log the change
        current_app.logger.info(
            f"Environment switched from {current_env} to {environment} "
            f"by user {user_id or 'unknown'}"
        )

        return {
            'success': True,
            'message': f'Environment switched to {environment}',
            'previous_environment': current_env,
            'new_environment': environment,
            'requires_restart': True,
            'restart_instructions': 'Please restart the backend server to apply changes'
        }

    @classmethod
    def toggle_maintenance(cls, enabled: bool, message: str = None, user_id: str = None) -> Dict:
        """
        Enable or disable maintenance mode

        Args:
            enabled: True to enable maintenance mode, False to disable
            message: Custom maintenance message (optional)
            user_id: User ID performing the action (for audit)

        Returns:
            Dict with success status and new state
        """
        current_state = cls.is_maintenance_mode()

        # Update maintenance mode setting
        success = SystemSettingsRepository.update_setting(
            'system.maintenance_mode',
            enabled,
            value_type='boolean'
        )

        if not success:
            # Create setting if it doesn't exist
            SystemSettingsRepository.create_setting(
                key='system.maintenance_mode',
                value=enabled,
                category='system',
                description='Maintenance mode flag',
                editable=True,
                value_type='boolean'
            )

        # Update custom message if provided
        if message:
            SystemSettingsRepository.update_setting(
                'system.maintenance_message',
                message,
                value_type='string'
            )
        elif enabled and not SystemSettingsRepository.setting_exists('system.maintenance_message'):
            # Set default message
            SystemSettingsRepository.create_setting(
                key='system.maintenance_message',
                value='System wird gewartet. Bitte versuchen Sie es später erneut.',
                category='system',
                description='Maintenance mode message',
                editable=True,
                value_type='string'
            )

        # If enabling maintenance, also enable debug for troubleshooting
        if enabled:
            SystemSettingsRepository.update_setting(
                'system.debug_enabled',
                True,
                value_type='boolean'
            )

        # Log the change
        action = 'enabled' if enabled else 'disabled'
        current_app.logger.warning(
            f"Maintenance mode {action} by user {user_id or 'unknown'}"
        )

        return {
            'success': True,
            'message': f'Maintenance mode {action}',
            'maintenance_enabled': enabled,
            'previous_state': current_state,
            'maintenance_message': message or cls.get_maintenance_message(),
            'debug_auto_enabled': enabled
        }

    @classmethod
    def get_system_status(cls) -> Dict:
        """
        Get comprehensive system status

        Returns:
            Dict with system status information
        """
        environment = cls.get_current_environment()
        debug_enabled = cls.is_debug_enabled()
        maintenance_mode = cls.is_maintenance_mode()
        uptime_seconds = int(time.time() - cls._start_time)
        version = current_app.config.get('LSX_VERSION', '1.0.0')

        # Check database connection
        db_connected = cls._check_database_connection()

        # Check Redis connection
        redis_connected = cls._check_redis_connection()

        return {
            'environment': environment,
            'debug_enabled': debug_enabled,
            'maintenance_mode': maintenance_mode,
            'uptime_seconds': uptime_seconds,
            'version': version,
            'database_connected': db_connected,
            'redis_connected': redis_connected,
            'timestamp': datetime.utcnow().isoformat()
        }

    @classmethod
    def get_current_environment(cls) -> str:
        """
        Get current environment from settings or config

        Returns:
            'development' or 'production'
        """
        # Try database first
        env_setting = SystemSettingsRepository.get_setting('system.environment')
        if env_setting:
            return env_setting

        # Fallback to config
        flask_env = current_app.config.get('LSX_ENV', 'development')
        return flask_env

    @classmethod
    def is_maintenance_mode(cls) -> bool:
        """
        Check if maintenance mode is enabled

        Returns:
            True if maintenance mode is active
        """
        mode = SystemSettingsRepository.get_setting('system.maintenance_mode')
        return mode == 'true' if mode else False

    @classmethod
    def is_debug_enabled(cls) -> bool:
        """
        Check if debug mode is enabled

        Returns:
            True if debug is enabled
        """
        debug = SystemSettingsRepository.get_setting('system.debug_enabled')
        if debug:
            return debug == 'true'

        # Fallback to config
        return current_app.config.get('DEBUG', False)

    @classmethod
    def get_maintenance_message(cls) -> str:
        """
        Get custom maintenance message or default

        Returns:
            Maintenance message string
        """
        message = SystemSettingsRepository.get_setting('system.maintenance_message')
        return message if message else 'System wird gewartet. Bitte versuchen Sie es später erneut.'

    @classmethod
    def validate_mode_change(cls, current_env: str, target_env: str) -> Dict:
        """
        Validate if mode change is safe

        Args:
            current_env: Current environment
            target_env: Target environment

        Returns:
            Dict with validation result and warnings
        """
        warnings = []

        if current_env == target_env:
            return {
                'valid': False,
                'reason': 'Already in target environment',
                'warnings': []
            }

        # Production → Development warnings
        if current_env == 'production' and target_env == 'development':
            warnings.append('Switching to development will enable debug mode')
            warnings.append('CORS will allow all origins')
            warnings.append('Rate limits will be relaxed')

        # Development → Production warnings
        if current_env == 'development' and target_env == 'production':
            warnings.append('Debug mode will be disabled')
            warnings.append('CORS will be restricted')
            warnings.append('Stricter security headers will be enforced')

        return {
            'valid': True,
            'warnings': warnings
        }

    @classmethod
    def _check_database_connection(cls) -> bool:
        """
        Check if database is connected

        Returns:
            True if database is reachable
        """
        try:
            from app.extensions import db_pool
            with db_pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute('SELECT 1')
                    return True
        except Exception:
            return False

    @classmethod
    def _check_redis_connection(cls) -> bool:
        """
        Check if Redis is connected

        Returns:
            True if Redis is reachable
        """
        try:
            from app.extensions import redis_client
            redis_client.ping()
            return True
        except Exception:
            return False
