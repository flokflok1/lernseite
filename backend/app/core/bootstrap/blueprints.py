"""
Blueprint Registration - Install-aware routing and health endpoints.

Extracted from app/__init__.py (Section 5) for DDD layer compliance.

Implements intelligent routing based on installation status:
- If not installed: Only Setup Wizard routes available
- If installed: Normal application routes via Gateway
"""

import os
import sys

from flask import Flask, jsonify


def register_blueprints(app: Flask) -> None:
    """
    Register Flask blueprints for API routes through the Gateway (Phase 21).

    Args:
        app: Flask application instance
    """
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

    from app.setup.diagnostics.install import InstallationChecker

    is_installed = InstallationChecker.is_installed()

    # ALWAYS register Setup Wizard (for status checks and reinstall)
    from app.setup import setup_bp
    app.register_blueprint(setup_bp)

    if is_installed:
        _register_installed_routes(app)
    else:
        _register_setup_wizard_routes(app)

    # Health check endpoints (always available)
    _register_health_endpoints(app)


def _register_installed_routes(app: Flask) -> None:
    """Register routes for an installed system."""
    app.logger.info('System installed - loading application routes via API Gateway')

    from app.api.gateway import register_gateway_routes
    register_gateway_routes(app)

    app.logger.info("ℹ AI Operations routes: Available via API Gateway")
    app.logger.info("✓ Social/Messaging/Community routes auto-registered via api_v1")

    @app.route('/')
    def index():
        """Root endpoint - redirect to API documentation"""
        return jsonify({
            'message': 'LernsystemX API',
            'version': '1.0.0',
            'status': 'running',
            'docs': '/api/v1/docs',
            'health': '/health'
        }), 200


def _register_setup_wizard_routes(app: Flask) -> None:
    """Register routes for setup wizard mode (system not installed)."""
    app.logger.warning('System not installed - Setup Wizard mode active')
    app.logger.info('Please navigate to http://localhost:5000/setup/status to begin installation')

    @app.route('/')
    def index():
        """Root endpoint - redirect to setup wizard"""
        return jsonify({
            'message': 'LernsystemX Setup Wizard',
            'status': 'not_installed',
            'setup_required': True,
            'instructions': 'Navigate to /setup/status to begin installation',
            'next_step': '/setup/check'
        }), 200

    @app.route('/setup/status')
    def setup_status():
        """Setup wizard status check - works without Redis"""
        return jsonify({
            'success': True,
            'status': 'not_installed',
            'setup_required': True,
            'message': 'LernsystemX is not yet configured',
            'instructions': 'Please complete the setup process',
            'requirements': {
                'database': {
                    'required': True,
                    'configured': bool(os.getenv('DATABASE_URL')),
                    'status': 'PostgreSQL connection required'
                },
                'redis': {
                    'required': False,
                    'configured': bool(os.getenv('REDIS_URL')),
                    'status': 'Optional - for caching and sessions'
                },
                'secret_key': {
                    'required': True,
                    'configured': os.getenv('SECRET_KEY') != 'your-secret-key-change-this-in-production',
                    'status': 'Update SECRET_KEY in .env file'
                }
            },
            'next_steps': [
                '1. Configure PostgreSQL database in .env file',
                '2. Update SECRET_KEY and JWT_SECRET_KEY in .env file',
                '3. (Optional) Configure Redis for caching',
                '4. Restart the backend server',
                '5. Run database migrations'
            ]
        }), 200

    @app.route('/setup/check')
    def setup_check():
        """Setup wizard environment check - works without Redis"""
        checks = {
            'database_url': {
                'status': 'configured' if os.getenv('DATABASE_URL') else 'missing',
                'value': os.getenv('DATABASE_URL', 'Not set'),
                'required': True
            },
            'secret_key': {
                'status': 'configured' if os.getenv('SECRET_KEY') != 'your-secret-key-change-this-in-production' else 'default',
                'required': True
            },
            'jwt_secret': {
                'status': 'configured' if os.getenv('JWT_SECRET_KEY') != 'your-jwt-secret-key-change-this' else 'default',
                'required': True
            },
            'redis_url': {
                'status': 'configured' if os.getenv('REDIS_URL') else 'missing',
                'value': os.getenv('REDIS_URL', 'Not set'),
                'required': False
            }
        }

        all_required_configured = all(
            check['status'] in ['configured', 'default']
            for check in checks.values()
            if check['required']
        )

        return jsonify({
            'success': True,
            'checks': checks,
            'ready_for_installation': all_required_configured,
            'message': 'Configuration check complete'
        }), 200


def _register_health_endpoints(app: Flask) -> None:
    """Register health check endpoints (always available, exempt from rate limiting)."""
    from app.api.v1.system.health import health_check, health_check_detailed, readiness_check, liveness_check
    from app.core.bootstrap.extensions import limiter

    @app.route('/health')
    @limiter.exempt
    def health():
        """Basic health check endpoint"""
        return health_check()

    @app.route('/health/detailed')
    @limiter.exempt
    def health_detailed():
        """Detailed health check endpoint"""
        return health_check_detailed()

    @app.route('/health/ready')
    @limiter.exempt
    def ready():
        """Readiness check for K8s"""
        return readiness_check()

    @app.route('/health/live')
    @limiter.exempt
    def live():
        """Liveness check for K8s"""
        return liveness_check()
