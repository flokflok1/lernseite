"""
Security Configuration - JWT, CORS, rate limiting, security headers.

Extracted from app/__init__.py (Section 2) for DDD layer compliance.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

from app.core.bootstrap.extensions import jwt


def configure_jwt(app: Flask) -> None:
    """
    Configure JWT extension with callbacks.

    Args:
        app: Flask application instance
    """
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
    Configure CORS for the application.

    Args:
        app: Flask application instance
    """
    CORS(
        app,
        origins=app.config['CORS_ORIGINS'],
        supports_credentials=True,
        allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
        expose_headers=['Content-Type', 'Authorization'],
        methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
        max_age=3600
    )

    @app.after_request
    def after_request(response):
        """Add CORS headers to all responses"""
        origin = request.headers.get('Origin')

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

    Args:
        app: Flask application instance
    """
    from app.infrastructure.security import init_rate_limiter, handle_rate_limit_exceeded

    init_rate_limiter(app)
    app.register_error_handler(429, handle_rate_limit_exceeded)


def setup_security_headers(app: Flask) -> None:
    """
    Setup security headers middleware (Phase 20).

    Args:
        app: Flask application instance
    """
    from app.api.middleware.security_headers import setup_security_headers as init_security_headers

    init_security_headers(app)
