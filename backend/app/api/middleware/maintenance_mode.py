"""
LernsystemX Middleware - Maintenance Mode Check

Intercepts requests when system is in maintenance mode.
Admins and superadmins can still access, regular users receive 503.

ISO 27001:2013 compliant
"""

from flask import request, jsonify, g
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def maintenance_mode_check():
    """
    Check if maintenance mode is active before each request

    - Runs before every request (except excluded paths)
    - Checks system.maintenance_mode setting
    - Allows admins and superadmins through
    - Returns 503 for regular users

    Excluded paths:
    - /setup/* (setup wizard)
    - /health (health check)
    - /api/v1/auth/login (login endpoint)
    - /static/* (static files)
    """
    # Import here to avoid circular dependency
    from app.application.services.system.mode.service import SystemModeService

    # Excluded paths that should work even in maintenance mode
    excluded_paths = [
        '/setup',
        '/health',
        '/api/v1/auth/login',
        '/api/v1/auth/refresh',
        '/static'
    ]

    # Check if current path is excluded
    current_path = request.path
    if any(current_path.startswith(path) for path in excluded_paths):
        return None

    # Check if maintenance mode is active
    if not SystemModeService.is_maintenance_mode():
        return None

    # Check if user is authenticated and is admin (RBAC 2.0: dynamic from DB)
    user = g.get('current_user')
    if user:
        from app.application.services.system.auth.permission import PermissionService
        if PermissionService.check_threshold(user, 'maintenance.access'):
            # Admin+ can access - add header to indicate maintenance mode
            g.maintenance_mode_active = True
            return None

    # Maintenance mode is active and user is not admin
    maintenance_message = SystemModeService.get_maintenance_message()

    logger.info(
        f"Maintenance mode: Blocked request to {current_path} "
        f"from {request.remote_addr}"
    )

    return jsonify({
        'success': False,
        'error': 'System maintenance',
        'message': maintenance_message,
        'maintenance_mode': True,
        'retry_after': 3600  # Suggest retry after 1 hour
    }), 503


def bypass_maintenance_for_admins(f):
    """
    Decorator to bypass maintenance mode check for specific routes

    Usage:
        @admin_bp.route('/critical-endpoint')
        @bypass_maintenance_for_admins
        def critical_endpoint():
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Mark this request as bypassing maintenance check
        g.bypass_maintenance = True
        return f(*args, **kwargs)
    return decorated_function


def get_maintenance_status() -> dict:
    """
    Get maintenance mode status for response headers

    Returns:
        Dict with maintenance mode info
    """
    from app.application.services.system.mode.service import SystemModeService

    is_maintenance = SystemModeService.is_maintenance_mode()

    if not is_maintenance:
        return {}

    return {
        'X-Maintenance-Mode': 'active',
        'X-Maintenance-Message': SystemModeService.get_maintenance_message()
    }


def add_maintenance_headers(response):
    """
    Add maintenance mode headers to response if active

    Args:
        response: Flask response object

    Returns:
        Modified response with maintenance headers
    """
    # Skip for excluded paths
    if request.path.startswith('/static'):
        return response

    # Add headers if maintenance is active
    headers = get_maintenance_status()
    for key, value in headers.items():
        response.headers[key] = value

    # If admin is accessing during maintenance, add warning header
    if g.get('maintenance_mode_active'):
        response.headers['X-Admin-Maintenance-Access'] = 'true'

    return response


def init_maintenance_middleware(app):
    """
    Register maintenance mode checks with Flask app

    Args:
        app: Flask application instance
    """
    # Register before_request handler
    @app.before_request
    def check_maintenance():
        """Check maintenance mode before each request"""
        # Skip if bypass flag is set
        if g.get('bypass_maintenance'):
            return None

        return maintenance_mode_check()

    # Register after_request handler for headers
    @app.after_request
    def add_headers(response):
        """Add maintenance headers to response"""
        return add_maintenance_headers(response)

    logger.info("Maintenance mode middleware initialized")
