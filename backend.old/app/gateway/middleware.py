"""
LernsystemX API Gateway - Middleware

Gateway-level middleware for request validation and processing.

Implements:
- Request size validation
- Content-Type validation
- Multi-tenant header processing
- Request ID generation

Based on Dok 32 (API-Gateway) - Phase 21
"""

from flask import Flask, request, jsonify, g
from werkzeug.exceptions import RequestEntityTooLarge
import uuid


def validate_request_size(app: Flask):
    """
    Validate request body size against configured maximum.

    Args:
        app: Flask application instance

    Returns:
        Error response if size exceeded, None otherwise
    """
    if not app.config.get('API_GATEWAY_ENABLED', True):
        return None

    max_size = app.config.get('API_GATEWAY_MAX_BODY_SIZE', 20 * 1024 * 1024)

    # Check Content-Length header
    content_length = request.content_length
    if content_length and content_length > max_size:
        return jsonify({
            'success': False,
            'error': 'Request Entity Too Large',
            'message': f'Request body exceeds maximum size of {max_size / (1024 * 1024):.0f}MB',
            'status_code': 413
        }), 413

    return None


def validate_content_type(app: Flask):
    """
    Validate Content-Type header for POST/PUT/PATCH requests.

    Args:
        app: Flask application instance

    Returns:
        Error response if invalid, None otherwise
    """
    if not app.config.get('API_GATEWAY_ENABLED', True):
        return None

    if not app.config.get('API_GATEWAY_VALIDATE_CONTENT_TYPE', True):
        return None

    # Only validate for methods with body
    if request.method not in ['POST', 'PUT', 'PATCH']:
        return None

    # Skip validation for certain endpoints
    skip_paths = ['/health', '/metrics']
    if any(request.path.startswith(path) for path in skip_paths):
        return None

    # Check Content-Type
    content_type = request.content_type
    if not content_type:
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': 'Missing Content-Type header',
            'status_code': 400
        }), 400

    # Must be application/json for JSON API
    if not content_type.startswith('application/json'):
        # Allow multipart/form-data for file uploads
        if not content_type.startswith('multipart/form-data'):
            return jsonify({
                'success': False,
                'error': 'Unsupported Media Type',
                'message': 'Content-Type must be application/json or multipart/form-data',
                'status_code': 415
            }), 415

    return None


def process_multi_tenant_headers(app: Flask):
    """
    Process multi-tenant headers (X-LSX-Org-ID, X-LSX-Client).

    Extracts organisation ID and client type from headers.

    Args:
        app: Flask application instance
    """
    if not app.config.get('API_GATEWAY_ENABLED', True):
        return

    if not app.config.get('API_GATEWAY_MULTI_TENANT_ENABLED', True):
        return

    # Extract org ID from header
    org_header = app.config.get('API_GATEWAY_DEFAULT_ORG_HEADER', 'X-LSX-Org-ID')
    org_id = request.headers.get(org_header)
    if org_id:
        g.gateway_org_id = org_id

    # Extract client type from header
    client_header = app.config.get('API_GATEWAY_CLIENT_HEADER', 'X-LSX-Client')
    client_type = request.headers.get(client_header)
    if client_type:
        g.gateway_client_type = client_type  # web|mobile|admin


def setup_gateway_middleware(app: Flask):
    """
    Setup all gateway middleware.

    Registers before_request handlers for:
    - Request size validation
    - Content-Type validation
    - Multi-tenant header processing

    Args:
        app: Flask application instance
    """
    if not app.config.get('API_GATEWAY_ENABLED', True):
        app.logger.info('Gateway middleware disabled')
        return

    app.logger.info('Setting up API Gateway middleware...')

    @app.before_request
    def gateway_before_request():
        """Run all gateway middleware before each request"""
        # Validate request size
        size_error = validate_request_size(app)
        if size_error:
            return size_error

        # Validate Content-Type
        content_type_error = validate_content_type(app)
        if content_type_error:
            return content_type_error

        # Process multi-tenant headers
        process_multi_tenant_headers(app)

        return None

    app.logger.info('Gateway middleware configured:')
    max_body_size = app.config.get('API_GATEWAY_MAX_BODY_SIZE', 20 * 1024 * 1024)
    app.logger.info(f"  - Request size limit: {max_body_size / (1024 * 1024):.0f}MB")
    app.logger.info(f"  - Content-Type validation: {app.config.get('API_GATEWAY_VALIDATE_CONTENT_TYPE', True)}")
    app.logger.info(f"  - Multi-tenant routing: {app.config.get('API_GATEWAY_MULTI_TENANT_ENABLED', True)}")
