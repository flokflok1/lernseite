"""
Middleware & Infrastructure - Monitoring, gateway, prompts, WebSocket events.

Extracted from app/__init__.py (Section 4) for DDD layer compliance.
"""

import sys

from flask import Flask, Response

from app.core.bootstrap.extensions import socketio


def setup_monitoring(app: Flask) -> None:
    """
    Setup monitoring and metrics collection (if enabled).

    Registers monitoring middleware, /metrics endpoint, and application info.

    Args:
        app: Flask application instance
    """
    if not app.config.get('MONITORING_ENABLED', False):
        app.logger.info('Monitoring disabled - skipping metrics setup')
        return

    app.logger.info('Setting up monitoring and metrics...')

    from app.api.middleware import setup_monitoring_middleware
    setup_monitoring_middleware(app)

    from app.infrastructure.monitoring import initialize_app_info

    initialize_app_info(
        version=app.config.get('LSX_VERSION', '1.0.0'),
        environment=app.config.get('LSX_ENV', 'development'),
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )

    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

    @app.route(app.config.get('MONITORING_METRICS_PATH', '/metrics'))
    def metrics():
        """Prometheus metrics endpoint"""
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    app.logger.info(f"Metrics endpoint registered at {app.config.get('MONITORING_METRICS_PATH', '/metrics')}")


def setup_gateway(app: Flask) -> None:
    """
    Setup API Gateway (Phase 21 + Phase 22).

    Args:
        app: Flask application instance
    """
    from app.api.gateway import setup_gateway_middleware, setup_gateway_versioning
    from app.api.gateway.analytics import setup_gateway_analytics
    from app.api.gateway.rate_limiting import setup_gateway_rate_limiting

    setup_gateway_middleware(app)
    setup_gateway_analytics(app)
    setup_gateway_rate_limiting(app)
    setup_gateway_versioning(app)


def setup_prompt_system(app: Flask) -> None:
    """
    Setup KI Prompt System (Phase 24).

    Args:
        app: Flask application instance
    """
    with app.app_context():
        try:
            from app.domain.ai.configuration.prompts.registry_bridge import init_default_prompts
            init_default_prompts()

            from app.domain.ai.configuration.prompts.ai_editor_prompts import init_ai_editor_prompts
            init_ai_editor_prompts()

            app.logger.info('KI Prompt System initialized successfully')
        except Exception as e:
            app.logger.error(f'Failed to initialize KI Prompt System: {str(e)}')


def register_socket_events(app: Flask) -> None:
    """
    Register WebSocket event handlers (Phase D4).

    Args:
        app: Flask application instance
    """
    try:
        from app.infrastructure.realtime.sockets import register_socket_events as register_events
        register_events(socketio)
        app.logger.info('WebSocket events registered successfully')
    except Exception as e:
        app.logger.error(f'Failed to register WebSocket events: {str(e)}')
