"""
LernsystemX API - Deprecation Management

Provides decorators and utilities for marking API endpoints as deprecated.

Implements:
- @deprecated decorator for endpoints
- Deprecation headers in responses
- Deprecation logging and tracking
- Sunset date enforcement

Based on Dok 33 (Versioning-Change-Management.md) - Phase 22
"""

from flask import current_app, request, g, make_response
from functools import wraps
from datetime import datetime
from typing import Optional, Callable
import warnings


class DeprecationWarning:
    """
    Deprecation warning information for an endpoint.
    """

    def __init__(
        self,
        deprecation_date: str,
        sunset_date: str,
        replacement: Optional[str] = None,
        migration_guide: Optional[str] = None,
        reason: Optional[str] = None
    ):
        """
        Initialize deprecation warning.

        Args:
            deprecation_date: ISO date when deprecation was announced (YYYY-MM-DD)
            sunset_date: ISO date when endpoint will be removed (YYYY-MM-DD)
            replacement: Optional replacement endpoint path
            migration_guide: Optional URL to migration guide
            reason: Optional reason for deprecation
        """
        self.deprecation_date = deprecation_date
        self.sunset_date = sunset_date
        self.replacement = replacement
        self.migration_guide = migration_guide
        self.reason = reason

    def is_sunset(self) -> bool:
        """
        Check if sunset date has passed.

        Returns:
            True if endpoint should be removed, False otherwise
        """
        try:
            sunset = datetime.fromisoformat(self.sunset_date)
            return datetime.utcnow() >= sunset
        except (ValueError, TypeError):
            return False

    def days_until_sunset(self) -> int:
        """
        Calculate days remaining until sunset.

        Returns:
            Number of days until sunset (negative if already sunset)
        """
        try:
            sunset = datetime.fromisoformat(self.sunset_date)
            delta = sunset - datetime.utcnow()
            return delta.days
        except (ValueError, TypeError):
            return -1


def deprecated(
    deprecation_date: str,
    sunset_date: str,
    replacement: Optional[str] = None,
    migration_guide: Optional[str] = None,
    reason: Optional[str] = None,
    enforce_sunset: bool = True
):
    """
    Decorator to mark an API endpoint as deprecated.

    Adds deprecation headers to response and logs usage of deprecated endpoint.
    Optionally enforces sunset date by returning 410 Gone after sunset.

    Args:
        deprecation_date: ISO date when deprecation was announced (YYYY-MM-DD)
        sunset_date: ISO date when endpoint will be removed (YYYY-MM-DD)
        replacement: Optional replacement endpoint path (e.g., "/api/v2/users")
        migration_guide: Optional URL to migration guide
        reason: Optional reason for deprecation
        enforce_sunset: If True, return 410 Gone after sunset date

    Returns:
        Decorated function

    Example:
        ```python
        @app.route('/api/v1/old-endpoint')
        @deprecated(
            deprecation_date='2025-06-01',
            sunset_date='2026-06-01',
            replacement='/api/v2/new-endpoint',
            reason='Replaced by improved v2 implementation'
        )
        def old_endpoint():
            return {'data': 'old'}
        ```

    Response headers:
        - X-LSX-Deprecated: true
        - X-LSX-Deprecation-Date: 2025-06-01
        - X-LSX-Sunset-Date: 2026-06-01
        - X-LSX-Replacement: /api/v2/new-endpoint (if provided)
        - X-LSX-Migration-Guide: URL (if provided)
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Create deprecation warning
            warning = DeprecationWarning(
                deprecation_date=deprecation_date,
                sunset_date=sunset_date,
                replacement=replacement,
                migration_guide=migration_guide,
                reason=reason
            )

            # Check if endpoint is sunset
            if enforce_sunset and warning.is_sunset():
                # Endpoint is past sunset date - return 410 Gone
                return _create_sunset_response(warning)

            # Log deprecation usage
            _log_deprecated_usage(request.path, warning)

            # Store deprecation info in request context for header addition
            g.deprecation_warning = warning

            # Call original endpoint
            response = f(*args, **kwargs)

            # Ensure response is a Response object
            if not hasattr(response, 'headers'):
                response = make_response(response)

            # Add deprecation headers
            response = _add_deprecation_headers(response, warning)

            return response

        # Mark function as deprecated (for introspection)
        decorated_function._deprecated = True
        decorated_function._deprecation_info = {
            'deprecation_date': deprecation_date,
            'sunset_date': sunset_date,
            'replacement': replacement,
            'migration_guide': migration_guide,
            'reason': reason
        }

        return decorated_function
    return decorator


def _create_sunset_response(warning: DeprecationWarning):
    """
    Create 410 Gone response for sunset endpoint.

    Args:
        warning: Deprecation warning information

    Returns:
        Flask response with 410 status
    """
    from flask import jsonify

    response_data = {
        'success': False,
        'error': 'Endpoint Sunset',
        'message': f'This endpoint was sunset on {warning.sunset_date}',
        'deprecation_date': warning.deprecation_date,
        'sunset_date': warning.sunset_date
    }

    if warning.replacement:
        response_data['replacement'] = warning.replacement

    if warning.migration_guide:
        response_data['migration_guide'] = warning.migration_guide

    if warning.reason:
        response_data['reason'] = warning.reason

    response = make_response(jsonify(response_data), 410)

    # Still add deprecation headers
    response = _add_deprecation_headers(response, warning)

    return response


def _add_deprecation_headers(response, warning: DeprecationWarning):
    """
    Add deprecation headers to response.

    Args:
        response: Flask response object
        warning: Deprecation warning information

    Returns:
        Response with deprecation headers
    """
    # Get header names from config
    deprecation_header = current_app.config.get('API_DEPRECATION_HEADER', 'X-LSX-Deprecated')
    deprecation_date_header = current_app.config.get('API_DEPRECATION_DATE_HEADER', 'X-LSX-Deprecation-Date')
    sunset_date_header = current_app.config.get('API_SUNSET_DATE_HEADER', 'X-LSX-Sunset-Date')
    replacement_header = current_app.config.get('API_REPLACEMENT_HEADER', 'X-LSX-Replacement')
    migration_guide_header = current_app.config.get('API_MIGRATION_GUIDE_HEADER', 'X-LSX-Migration-Guide')

    # Add headers
    response.headers[deprecation_header] = 'true'
    response.headers[deprecation_date_header] = warning.deprecation_date
    response.headers[sunset_date_header] = warning.sunset_date

    if warning.replacement:
        response.headers[replacement_header] = warning.replacement

    if warning.migration_guide:
        response.headers[migration_guide_header] = warning.migration_guide
    elif current_app.config.get('API_DEPRECATION_NOTICE_URL'):
        # Fallback to default deprecation notice URL
        default_url = current_app.config.get('API_DEPRECATION_NOTICE_URL')
        response.headers[migration_guide_header] = default_url

    # Add days until sunset as custom header (helpful for monitoring)
    days_until_sunset = warning.days_until_sunset()
    if days_until_sunset >= 0:
        response.headers['X-LSX-Days-Until-Sunset'] = str(days_until_sunset)

    return response


def _log_deprecated_usage(endpoint: str, warning: DeprecationWarning):
    """
    Log usage of deprecated endpoint.

    Logs include:
    - Endpoint path
    - User ID (if authenticated)
    - IP address
    - Days until sunset
    - Deprecation info

    Args:
        endpoint: Endpoint path
        warning: Deprecation warning information
    """
    # Get user info if authenticated
    user_id = None
    if hasattr(g, 'current_user') and g.current_user:
        user_id = g.current_user.get('user_id')

    # Build log data
    log_data = {
        'event': 'deprecated_endpoint_usage',
        'endpoint': endpoint,
        'method': request.method,
        'user_id': user_id,
        'ip': request.remote_addr,
        'deprecation_date': warning.deprecation_date,
        'sunset_date': warning.sunset_date,
        'days_until_sunset': warning.days_until_sunset(),
        'replacement': warning.replacement,
        'user_agent': request.headers.get('User-Agent', 'unknown')
    }

    # Log as warning (deprecated endpoints should be monitored)
    current_app.logger.warning(f"Deprecated endpoint usage: {log_data}")

    # TODO: In production, consider tracking this in metrics/analytics
    # Example: Increment Prometheus counter for deprecated endpoint usage
    # deprecated_endpoint_calls.labels(endpoint=endpoint, days_until_sunset=warning.days_until_sunset()).inc()


def is_endpoint_deprecated(func: Callable) -> bool:
    """
    Check if an endpoint function is marked as deprecated.

    Args:
        func: Endpoint function

    Returns:
        True if deprecated, False otherwise
    """
    return hasattr(func, '_deprecated') and func._deprecated


def get_deprecation_info(func: Callable) -> Optional[dict]:
    """
    Get deprecation information for an endpoint function.

    Args:
        func: Endpoint function

    Returns:
        Deprecation info dict or None if not deprecated
    """
    if is_endpoint_deprecated(func):
        return getattr(func, '_deprecation_info', None)
    return None


def list_deprecated_endpoints(app) -> list:
    """
    List all deprecated endpoints in the application.

    Useful for generating deprecation reports.

    Args:
        app: Flask application instance

    Returns:
        List of deprecated endpoint information
    """
    deprecated_endpoints = []

    for rule in app.url_map.iter_rules():
        if rule.endpoint and rule.endpoint != 'static':
            view_func = app.view_functions.get(rule.endpoint)
            if view_func and is_endpoint_deprecated(view_func):
                info = get_deprecation_info(view_func)
                if info:
                    deprecated_endpoints.append({
                        'endpoint': rule.endpoint,
                        'path': rule.rule,
                        'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                        **info
                    })

    return deprecated_endpoints
