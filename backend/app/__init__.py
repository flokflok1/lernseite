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
from flask import Flask, jsonify, request, Response
from werkzeug.exceptions import HTTPException

from app.core.bootstrap.config import config
from app.infrastructure.i18n.error_codes import ErrorCode, error_response

# ============================================================================
# SECTION 1: EXTENSIONS INITIALIZATION
# ============================================================================

from app.core.bootstrap.extensions import (
    db_pool,
    init_db_pool,
    jwt,
    socketio,
    celery,
    redis_client,
    limiter,
    mail
)


def register_extensions(app: Flask) -> None:
    """
    Register Flask extensions

    Args:
        app (Flask): Flask application instance
    """
    # Database Connection Pool (psycopg)
    init_db_pool(
        database_url=app.config['SQLALCHEMY_DATABASE_URI'],
        min_size=app.config.get('DB_POOL_MIN_SIZE', 2),
        max_size=app.config.get('DB_POOL_MAX_SIZE', 10)
    )

    # Authentication
    jwt.init_app(app)

    # WebSocket
    socketio.init_app(
        app,
        message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'],
        cors_allowed_origins=app.config['SOCKETIO_CORS_ALLOWED_ORIGINS']
    )

    # Rate Limiting
    limiter.init_app(app)

    # Email (Legacy Flask-Mail)
    mail.init_app(app)

    # Email Service (New Template-based Email Utility)
    from app.utils.email import init_email_service
    init_email_service(app)


def register_shell_context(app: Flask) -> None:
    """
    Register shell context for Flask shell

    Args:
        app (Flask): Flask application instance
    """
    @app.shell_context_processor
    def make_shell_context():
        """Add database pool and utilities to shell context"""
        from app.infrastructure.persistence.repositories.user import UserRepository
        from app.infrastructure.persistence.repositories.courses import CourseRepository
        from app.infrastructure.persistence.repositories.courses.chapters import ChapterRepository
        from app.infrastructure.persistence.repositories.courses.lessons import LessonRepository
        from app.infrastructure.persistence.repositories.enrollments.core import EnrollmentRepository
        from app.infrastructure.persistence.repositories.category import CategoryRepository
        from app.infrastructure.persistence.repositories.learning_method import LearningMethodRepository
        from app.infrastructure.persistence.repositories.token import TokenRepository
        from app.infrastructure.persistence.repositories.subscription import SubscriptionRepository
        from app.infrastructure.persistence.repositories.organisations.core import OrganisationRepository
        from app.infrastructure.persistence.repositories.dashboard.core import DashboardRepository
        from app.infrastructure.persistence.repositories.analytics import AnalyticsRepository
        from app.application.services.ai_adapter import AIAdapter
        from app.application.services.system.billing.service import BillingService

        return {
            'db_pool': db_pool,
            'redis': redis_client,
            'UserRepository': UserRepository,
            'CourseRepository': CourseRepository,
            'ChapterRepository': ChapterRepository,
            'LessonRepository': LessonRepository,
            'EnrollmentRepository': EnrollmentRepository,
            'CategoryRepository': CategoryRepository,
            'LearningMethodRepository': LearningMethodRepository,
            'TokenRepository': TokenRepository,
            'SubscriptionRepository': SubscriptionRepository,
            'OrganisationRepository': OrganisationRepository,
            'DashboardRepository': DashboardRepository,
            'AnalyticsRepository': AnalyticsRepository,
            'AIAdapter': AIAdapter,
            'BillingService': BillingService
        }


def init_celery(app: Flask) -> None:
    """
    Initialize Celery with Flask app context

    Args:
        app (Flask): Flask application instance
    """
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask


# ============================================================================
# SECTION 2: SECURITY CONFIGURATION
# ============================================================================

from flask_cors import CORS


def configure_jwt(app: Flask) -> None:
    """
    Configure JWT extension with callbacks

    Args:
        app (Flask): Flask application instance
    """
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handle expired tokens"""
        return jsonify({
            'success': False,
            'error': 'Token expired',
            'message': 'Your session has expired. Please login again.'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Handle invalid tokens"""
        return jsonify({
            'success': False,
            'error': 'Invalid token',
            'message': 'The token provided is invalid.'
        }), 401

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        """Handle missing tokens"""
        return jsonify({
            'success': False,
            'error': 'Authorization required',
            'message': 'Missing authorization token. Please login.'
        }), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        """Handle revoked tokens"""
        return jsonify({
            'success': False,
            'error': 'Token revoked',
            'message': 'This token has been revoked. Please login again.'
        }), 401

    @jwt.needs_fresh_token_loader
    def needs_fresh_token_callback(jwt_header, jwt_payload):
        """Handle non-fresh tokens"""
        return jsonify({
            'success': False,
            'error': 'Fresh token required',
            'message': 'This operation requires a fresh token. Please re-authenticate.'
        }), 401

    # TODO: Implement token blacklist check
    # @jwt.token_in_blocklist_loader
    # def check_if_token_revoked(jwt_header, jwt_payload):
    #     jti = jwt_payload['jti']
    #     return redis_client.get(f"blacklist:{jti}") is not None


def configure_cors(app: Flask) -> None:
    """
    Configure CORS for the application

    Args:
        app (Flask): Flask application instance
    """
    CORS(
        app,
        origins=app.config['CORS_ORIGINS'],
        supports_credentials=True,
        allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
        expose_headers=['Content-Type', 'Authorization'],
        methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
        max_age=3600  # Cache preflight requests for 1 hour
    )

    # Add global OPTIONS handler for all routes
    @app.after_request
    def after_request(response):
        """Add CORS headers to all responses"""
        origin = request.headers.get('Origin')

        # Allow configured origins
        if origin:
            allowed_origins = app.config.get('CORS_ORIGINS', ['*'])
            if '*' in allowed_origins or origin in allowed_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
                response.headers['Access-Control-Max-Age'] = '3600'

        return response


def setup_rate_limiting(app: Flask) -> None:
    """
    Setup rate limiting and brute-force protection (Phase 20).

    Initializes rate limiting configuration and registers error handlers.

    Args:
        app (Flask): Flask application instance
    """
    from app.infrastructure.security import init_rate_limiter, handle_rate_limit_exceeded

    # Initialize rate limiter
    init_rate_limiter(app)

    # Register rate limit error handler
    app.register_error_handler(429, handle_rate_limit_exceeded)


def setup_security_headers(app: Flask) -> None:
    """
    Setup security headers middleware (Phase 20).

    Adds security headers to all HTTP responses to protect against:
    - Clickjacking (X-Frame-Options)
    - MIME-sniffing (X-Content-Type-Options)
    - XSS attacks (X-XSS-Protection, CSP)
    - Protocol downgrade (HSTS)

    Args:
        app (Flask): Flask application instance
    """
    from app.api.middleware.security_headers import setup_security_headers as init_security_headers

    # Initialize security headers
    init_security_headers(app)


# ============================================================================
# SECTION 3: ERROR HANDLERS
# ============================================================================

def register_error_handlers(app: Flask) -> None:
    """
    Register global error handlers

    Args:
        app (Flask): Flask application instance
    """
    from pydantic import ValidationError
    from app.infrastructure.utils.exceptions import APIException

    @app.errorhandler(APIException)
    def handle_api_exception(error):
        """Handle custom API exceptions"""
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle Pydantic validation errors"""
        return error_response(
            ErrorCode.VALIDATION_ERROR,
            status=400,
            details={'validation_errors': error.errors()}
        )

    @app.errorhandler(ValueError)
    def handle_value_error(error):
        """Handle ValueError exceptions"""
        return error_response(
            ErrorCode.BAD_REQUEST,
            status=400,
            details={'value_error': str(error)}
        )

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle HTTP exceptions"""
        # Map HTTP error codes to ErrorCode enum values
        error_code_map = {
            400: ErrorCode.BAD_REQUEST,
            401: ErrorCode.UNAUTHORIZED,
            403: ErrorCode.FORBIDDEN,
            404: ErrorCode.NOT_FOUND,
            405: ErrorCode.FORBIDDEN,  # Method not allowed
            429: ErrorCode.BAD_REQUEST,  # Rate limit
            500: ErrorCode.INTERNAL_ERROR,
            503: ErrorCode.INTERNAL_ERROR,
        }
        error_code = error_code_map.get(error.code, ErrorCode.INTERNAL_ERROR)
        return error_response(
            error_code,
            status=error.code,
            details={'http_error': error.name}
        )

    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle general exceptions"""
        app.logger.error(f'Unhandled exception: {str(error)}')
        details = {}
        # Only include details in development
        if app.config.get('DEBUG'):
            details['error_detail'] = str(error)
        return error_response(
            ErrorCode.INTERNAL_ERROR,
            status=500,
            details=details
        )

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return error_response(ErrorCode.NOT_FOUND, status=404)

    @app.errorhandler(429)
    def ratelimit_handler(error):
        """Handle rate limit exceeded"""
        return error_response(
            ErrorCode.BAD_REQUEST,
            status=429,
            details={'reason': 'rate_limit_exceeded'}
        )

    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 errors"""
        return error_response(ErrorCode.BAD_REQUEST, status=400)

    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 errors"""
        return error_response(ErrorCode.UNAUTHORIZED, status=401)

    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 errors"""
        return error_response(ErrorCode.FORBIDDEN, status=403)

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors"""
        return error_response(
            ErrorCode.FORBIDDEN,
            status=405,
            details={'reason': 'method_not_allowed'}
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 errors"""
        app.logger.error(f'Internal server error: {str(error)}')
        return error_response(ErrorCode.INTERNAL_ERROR, status=500)


# ============================================================================
# SECTION 4: MIDDLEWARE & INFRASTRUCTURE
# ============================================================================

def setup_monitoring(app: Flask) -> None:
    """
    Setup monitoring and metrics collection (if enabled)

    Registers:
    - Monitoring middleware for automatic HTTP request instrumentation
    - /metrics endpoint for Prometheus scraping
    - Application info metrics

    Args:
        app (Flask): Flask application instance
    """
    if not app.config.get('MONITORING_ENABLED', False):
        app.logger.info('Monitoring disabled - skipping metrics setup')
        return

    app.logger.info('Setting up monitoring and metrics...')

    # Setup monitoring middleware
    from app.api.middleware import setup_monitoring_middleware
    setup_monitoring_middleware(app)

    # Initialize application info metric
    from app.infrastructure.monitoring import initialize_app_info
    import sys

    initialize_app_info(
        version=app.config.get('LSX_VERSION', '1.0.0'),
        environment=app.config.get('LSX_ENV', 'development'),
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )

    # Register /metrics endpoint
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

    @app.route(app.config.get('MONITORING_METRICS_PATH', '/metrics'))
    def metrics():
        """
        Prometheus metrics endpoint

        Returns all collected metrics in Prometheus format.
        This endpoint should be restricted via Nginx (IP whitelist or Basic Auth).

        Returns:
            Response: Metrics in Prometheus text format
        """
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    app.logger.info(f"Metrics endpoint registered at {app.config.get('MONITORING_METRICS_PATH', '/metrics')}")


def setup_gateway(app: Flask) -> None:
    """
    Setup API Gateway (Phase 21 + Phase 22).

    Initializes:
    - Gateway routing and segmentation
    - Gateway-level middleware
    - Gateway analytics and logging
    - Gateway rate limiting
    - API versioning and deprecation management (Phase 22)

    Args:
        app (Flask): Flask application instance
    """
    from app.api.gateway import setup_gateway_middleware, setup_gateway_versioning
    from app.api.gateway.analytics import setup_gateway_analytics
    from app.api.gateway.rate_limiting import setup_gateway_rate_limiting

    # Setup gateway middleware (request validation)
    setup_gateway_middleware(app)

    # Setup gateway analytics (request tracking)
    setup_gateway_analytics(app)

    # Setup gateway rate limiting
    setup_gateway_rate_limiting(app)

    # Setup API versioning (Phase 22)
    setup_gateway_versioning(app)

    # Register routes through gateway (called in register_blueprints)
    # Note: Actual route registration happens in register_blueprints()
    # This is just initialization


def setup_prompt_system(app: Flask) -> None:
    """
    Setup KI Prompt System (Phase 24).

    Initializes central prompt registry with default templates for:
    - explain_concept
    - flashcards
    - quiz_generator
    - socratic_tutor
    - summarize_lesson
    - translation_assistant

    Args:
        app (Flask): Flask application instance
    """
    with app.app_context():
        try:
            from app.domain.ai.configuration.prompt_registry import init_default_prompts
            init_default_prompts()

            # Initialize AI Editor prompts (Phase D4)
            from app.domain.ai.configuration.ai_editor_prompts import init_ai_editor_prompts
            init_ai_editor_prompts()

            app.logger.info('KI Prompt System initialized successfully')
        except Exception as e:
            app.logger.error(f'Failed to initialize KI Prompt System: {str(e)}')
            # Don't fail app startup, just log the error
            # Prompts can be registered later if needed


def register_socket_events(app: Flask) -> None:
    """
    Register WebSocket event handlers (Phase D4).

    Initializes SocketIO namespaces for:
    - AI Editor real-time updates (/ai-editor)

    Args:
        app (Flask): Flask application instance
    """
    try:
        from app.infrastructure.realtime.sockets import register_socket_events as register_events
        register_events(socketio)
        app.logger.info('WebSocket events registered successfully')
    except Exception as e:
        app.logger.error(f'Failed to register WebSocket events: {str(e)}')
        # Don't fail app startup, just log the error


# ============================================================================
# SECTION 5: BLUEPRINT REGISTRATION
# ============================================================================

def register_blueprints(app):
    """
    Register Flask blueprints for API routes through the Gateway (Phase 21).

    Implements intelligent routing based on installation status:
    - If not installed: Only Setup Wizard routes available
    - If installed: Normal application routes via Gateway

    Args:
        app (Flask): Flask application instance
    """
    # Check if system is installed
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))

    from app.setup.install_check import InstallationChecker

    is_installed = InstallationChecker.is_installed()

    # ALWAYS register Setup Wizard (for status checks and reinstall)
    from app.setup import setup_bp
    app.register_blueprint(setup_bp)

    if is_installed:
        # System is installed - register routes through Gateway (Phase 21)
        app.logger.info('System installed - loading application routes via API Gateway')

        # Register all routes through the API Gateway
        from app.api.gateway import register_gateway_routes
        register_gateway_routes(app)

        # Future API Blueprints:
        # Course routes (Phase 9)
        # from app.api.user.courses import courses_bp
        # app.register_blueprint(courses_bp)

        # Organisation routes (Phase 10)
        # from app.api.shared.organisations import organisations_bp
        # app.register_blueprint(organisations_bp)

        # AI Operations routes (Admin) - TODO: Complete refactoring needed
        # These blueprints are still being migrated and have missing dependencies
        # For now, endpoints are registered via api_v1 blueprint in app/api/admin/
        app.logger.info("ℹ AI Operations routes: Available via API Gateway")

        # Payment routes (Phase 12)
        # from app.api.payments import payments_bp
        # app.register_blueprint(payments_bp)

        # Social, Messaging, Community routes now registered via api_v1
        # See: app/api/social/__init__.py, app/api/messaging/__init__.py, app/api/community/__init__.py
        app.logger.info("✓ Social/Messaging/Community routes auto-registered via api_v1")

        # LiveRoom routes (Phase 14)
        # from app.api.liveroom import liveroom_bp
        # app.register_blueprint(liveroom_bp)

        # Root redirect to frontend or API docs
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

    else:
        # System NOT installed - Setup Wizard mode
        app.logger.warning('System not installed - Setup Wizard mode active')
        app.logger.info('Please navigate to http://localhost:5000/setup/status to begin installation')

        # Redirect root to setup wizard
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

        # Setup Wizard endpoints (without Redis dependency)
        @app.route('/setup/status')
        def setup_status():
            """Setup wizard status check - works without Redis"""
            import os
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
            import os

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

    # Health check endpoints (always available)
    from app.api.v1.system.health import health_check, health_check_detailed, readiness_check, liveness_check

    @app.route('/health')
    def health():
        """Basic health check endpoint"""
        return health_check()

    @app.route('/health/detailed')
    def health_detailed():
        """Detailed health check endpoint"""
        return health_check_detailed()

    @app.route('/health/ready')
    def ready():
        """Readiness check for K8s"""
        return readiness_check()

    @app.route('/health/live')
    def live():
        """Liveness check for K8s"""
        return liveness_check()


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

    return app
