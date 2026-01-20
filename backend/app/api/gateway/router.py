"""
LernsystemX API Gateway - Central Router

Implements centralized routing for all API endpoints based on Dok 32.

Route Segmentation:
- /api/v1/public/*     - Public APIs (limited access, no auth required)
- /api/v1/*            - App/User APIs (authenticated users)
- /api/v1/admin/*      - Admin APIs (system admins only)
- /api/v1/organisations/* - Organisation APIs (org members/admins)

Phase 21 - API Gateway
"""

from flask import Flask, Blueprint
from typing import Dict, List


class APIGateway:
    """
    Central API Gateway Router for LernsystemX.

    Manages route registration, segmentation, and organization.
    """

    def __init__(self, app: Flask = None):
        """Initialize API Gateway"""
        self.app = app
        self.registered_apps = set()  # Track which app instances have had routes registered

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """
        Initialize gateway with Flask app.

        Args:
            app: Flask application instance
        """
        self.app = app

        if not app.config.get('API_GATEWAY_ENABLED', True):
            app.logger.warning('API Gateway is DISABLED')
            return

        app.logger.info('Initializing API Gateway...')

    def register_routes(self, app: Flask):
        """
        Register all API routes through the gateway.

        Creates route segmentation:
        - Public APIs
        - App/User APIs
        - Admin APIs
        - Organisation APIs

        Args:
            app: Flask application instance
        """
        app_id = id(app)
        if app_id in self.registered_apps:
            app.logger.warning('Gateway routes already registered for this app, skipping...')
            return

        app.logger.info('=' * 60)
        app.logger.info('API GATEWAY - Registering Routes')
        app.logger.info('=' * 60)

        # Import existing blueprints
        from app.api import api_v1

        # Register main API blueprint (already includes all routes)
        # This maintains backward compatibility with existing routes
        app.register_blueprint(api_v1)

        app.logger.info(f"✓ Main API Blueprint registered: {api_v1.url_prefix}")

        # Log route groups for gateway analytics
        self._log_route_groups(app)

        self.registered_apps.add(app_id)
        app.logger.info('=' * 60)
        app.logger.info('API Gateway - Route Registration Complete')
        app.logger.info('=' * 60)

    def _log_route_groups(self, app: Flask):
        """
        Log registered route groups for monitoring and analytics.

        Args:
            app: Flask application instance
        """
        route_groups = self._get_route_groups()

        app.logger.info('')
        app.logger.info('Route Groups:')
        for group, routes in route_groups.items():
            app.logger.info(f'  {group}:')
            for route in routes:
                app.logger.info(f'    - {route}')

    def _get_route_groups(self) -> Dict[str, List[str]]:
        """
        Get organized route groups for the gateway.

        Returns:
            Dict mapping route group names to route prefixes
        """
        return {
            'Public APIs': [
                '/api/v1/public/*',
            ],
            'Authentication': [
                '/api/v1/auth/*',
            ],
            'User/App APIs': [
                '/api/v1/users/*',
                '/api/v1/profile/*',
                '/api/v1/courses/*',
                '/api/v1/categories/*',
                '/api/v1/methods/*',
                '/api/v1/subscriptions/*',
                '/api/v1/tokens/*',
                '/api/v1/dashboard/*',
                '/api/v1/analytics/*',
            ],
            'Admin APIs': [
                '/api/v1/admin/analytics/*',
                '/api/v1/admin/users/*',
                '/api/v1/admin/organisations/*',
            ],
            'Organisation APIs': [
                '/api/v1/organisations/*',
                '/api/v1/org/analytics/*',
            ],
            'Health & System': [
                '/health',
                '/health/detailed',
                '/health/ready',
                '/health/live',
                '/metrics',
            ],
        }

    def get_route_group(self, path: str) -> str:
        """
        Determine which route group a path belongs to.

        Args:
            path: Request path

        Returns:
            Route group name (public|app|admin|org|health)
        """
        if path.startswith('/api/v1/public'):
            return 'public'
        elif path.startswith('/api/v1/admin'):
            return 'admin'
        elif path.startswith('/api/v1/organisations') or path.startswith('/api/v1/org'):
            return 'org'
        elif path.startswith('/api/v1/auth'):
            return 'auth'
        elif path.startswith('/api/v1'):
            return 'app'
        elif path.startswith('/health') or path == '/metrics':
            return 'health'
        else:
            return 'unknown'


# Global gateway instance
_gateway = APIGateway()


def register_gateway_routes(app: Flask):
    """
    Register all routes through the API Gateway.

    This is the main entry point called from the Flask factory.

    Args:
        app: Flask application instance
    """
    _gateway.init_app(app)
    _gateway.register_routes(app)


def get_route_group(path: str) -> str:
    """
    Helper function to get route group for a given path.

    Args:
        path: Request path

    Returns:
        Route group name
    """
    return _gateway.get_route_group(path)
