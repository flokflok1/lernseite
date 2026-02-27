"""
LernsystemX Backend - Flask Application Factory

Comprehensive application initialization implementing the factory pattern
for creating Flask application instances supporting multiple configurations
(development, production, testing).

Coordinates initialization of:
- Flask extensions (database, JWT, WebSocket, rate limiting, mail)
- Security configuration (CORS, JWT callbacks, rate limiting, security headers)
- Middleware (monitoring, API gateway, KI prompts, WebSocket)
- Error handlers (custom exceptions, HTTP status codes)
- Blueprints (API routes through gateway)
- Shell context (utilities for Flask shell)

Architecture:
- Modular initialization functions
- Clear separation of concerns
- Proper error handling and logging
- Support for multiple environments
"""

import os
from flask import Flask

from app.core.bootstrap.config import config

# ============================================================================
# SECTION 1: EXTENSIONS INITIALIZATION  (extracted → core/bootstrap/init_extensions.py)
# ============================================================================

from app.core.bootstrap.extensions import socketio   # re-export for run.py
from app.core.bootstrap.init_extensions import (
    register_extensions,
    register_shell_context,
    init_celery,
)


# ============================================================================
# SECTION 2: SECURITY CONFIGURATION  (extracted → core/bootstrap/security.py)
# ============================================================================

from app.core.bootstrap.security import (
    configure_jwt,
    configure_cors,
    setup_rate_limiting,
    setup_security_headers,
)


# ============================================================================
# SECTION 3: ERROR HANDLERS  (extracted → core/bootstrap/error_handlers.py)
# ============================================================================

from app.core.bootstrap.error_handlers import register_error_handlers


# ============================================================================
# SECTION 4: MIDDLEWARE & INFRASTRUCTURE  (extracted → core/bootstrap/middleware.py)
# ============================================================================

from app.core.bootstrap.middleware import (
    setup_monitoring,
    setup_gateway,
    setup_prompt_system,
    register_socket_events,
)


# ============================================================================
# SECTION 5: BLUEPRINT REGISTRATION  (extracted → core/bootstrap/blueprints.py)
# ============================================================================

from app.core.bootstrap.blueprints import register_blueprints
from app.core.bootstrap.container import wire_repositories


# ============================================================================
# SECTION 6: APPLICATION FACTORY
# ============================================================================

def create_app(config_name=None):
    """
    Application Factory Pattern

    Creates and initializes a fully configured Flask application instance
    with all extensions, security, middleware, and blueprints registered.

    Args:
        config_name (str): Configuration name ('development', 'production', 'testing')
                          Defaults to FLASK_ENV environment variable or 'development'

    Returns:
        Flask: Configured Flask application instance
    """
    # Determine configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    # Initialize Flask app
    app = Flask(__name__, instance_relative_config=True)

    # Disable strict slashes to prevent 308 redirects on API endpoints
    # This fixes CORS preflight issues when clients request /path without trailing slash
    app.url_map.strict_slashes = False

    # Load configuration
    app.config.from_object(config[config_name])

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs('logs', exist_ok=True)
    except OSError:
        pass

    # Initialize extensions (Section 1)
    register_extensions(app)

    # Wire DI container (domain ports → infrastructure repos)
    wire_repositories()

    # Configure JWT callbacks (Section 2)
    configure_jwt(app)

    # Setup API Gateway (Section 4) - BEFORE blueprint registration
    setup_gateway(app)

    # Register blueprints (Section 5)
    register_blueprints(app)

    # Register error handlers (Section 3)
    register_error_handlers(app)

    # Configure CORS (Section 2)
    configure_cors(app)

    # Register shell context (Section 1)
    register_shell_context(app)

    # Initialize Celery (Section 1)
    init_celery(app)

    # Setup monitoring (Section 4) - if enabled
    setup_monitoring(app)

    # Setup rate limiting & brute-force protection (Section 2)
    setup_rate_limiting(app)

    # Setup security headers (Section 2)
    setup_security_headers(app)

    # Initialize KI Prompt System (Section 4)
    setup_prompt_system(app)

    # Register WebSocket events (Section 4)
    register_socket_events(app)

    # Seed default AI providers (idempotent)
    try:
        from app.infrastructure.persistence.repositories.ai.providers import AIProviderRepository
        seeded = AIProviderRepository.seed_defaults()
        if seeded > 0:
            app.logger.info(f'Seeded {seeded} default AI provider(s)')
    except Exception as e:
        app.logger.warning(f'Could not seed AI providers: {e}')

    return app
