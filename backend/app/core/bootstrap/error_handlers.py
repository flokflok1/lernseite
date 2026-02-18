"""
Error Handlers - Global Flask error handler registration.

Extracted from app/__init__.py (Section 3) for DDD layer compliance.
Registers handlers for: APIException, ValidationError, ValueError,
HTTPException, generic Exception, and status codes 400-500.
"""

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from app.infrastructure.i18n.error_codes import ErrorCode, error_response


def register_error_handlers(app: Flask) -> None:
    """
    Register global error handlers.

    Args:
        app: Flask application instance
    """
    from pydantic import ValidationError
    from app.infrastructure.error_handling.exceptions import APIException

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
        error_code_map = {
            400: ErrorCode.BAD_REQUEST,
            401: ErrorCode.UNAUTHORIZED,
            403: ErrorCode.FORBIDDEN,
            404: ErrorCode.NOT_FOUND,
            405: ErrorCode.FORBIDDEN,
            429: ErrorCode.BAD_REQUEST,
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
