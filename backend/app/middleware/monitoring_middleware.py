"""
LernsystemX - Monitoring Middleware

Flask middleware for automatic HTTP request instrumentation.
Records request metrics for Prometheus monitoring.

Based on Dok 30 (30_Monitoring-Alerting.md)
"""

import time
import logging
from flask import request, g
from functools import wraps
from typing import Callable, Any

from app.infrastructure.monitoring import record_http_request

logger = logging.getLogger(__name__)


def setup_monitoring_middleware(app):
    """
    Set up monitoring middleware for the Flask application.

    This registers before_request and after_request handlers to track
    HTTP request metrics automatically.

    Args:
        app: Flask application instance
    """

    @app.before_request
    def before_request_monitoring():
        """
        Record request start time before processing the request.
        """
        g.request_start_time = time.time()

    @app.after_request
    def after_request_monitoring(response):
        """
        Record request metrics after processing the request.

        Args:
            response: Flask response object

        Returns:
            Unmodified response object
        """
        # Skip monitoring for certain endpoints
        if should_skip_monitoring(request.path):
            return response

        # Calculate request duration
        request_duration = 0.0
        if hasattr(g, 'request_start_time'):
            request_duration = time.time() - g.request_start_time

        # Normalize endpoint for metrics (avoid high cardinality)
        endpoint = normalize_endpoint(request.path)

        # Record the HTTP request metrics
        try:
            record_http_request(
                method=request.method,
                endpoint=endpoint,
                status_code=response.status_code,
                duration=request_duration
            )
        except Exception as e:
            # Don't let monitoring errors affect the request
            logger.error(f"Error recording request metrics: {e}", exc_info=True)

        return response


def should_skip_monitoring(path: str) -> bool:
    """
    Determine if a request path should skip monitoring.

    Skip monitoring for:
    - /metrics endpoint itself (avoid recursion)
    - Static files
    - Health check endpoints (high frequency, low value)

    Args:
        path: Request path

    Returns:
        True if monitoring should be skipped
    """
    skip_paths = [
        '/metrics',
        '/static/',
        '/favicon.ico',
        '/health/live',  # Kubernetes liveness (very frequent)
    ]

    for skip_path in skip_paths:
        if path.startswith(skip_path):
            return True

    return False


def normalize_endpoint(path: str) -> str:
    """
    Normalize endpoint path to avoid high cardinality in metrics.

    Replaces dynamic segments (IDs, UUIDs) with placeholders to prevent
    creating too many unique metric label combinations.

    Examples:
        /api/courses/123 -> /api/courses/{id}
        /api/users/abc-123-def/profile -> /api/users/{id}/profile
        /api/lessons/456/content -> /api/lessons/{id}/content

    Args:
        path: Original request path

    Returns:
        Normalized path with placeholders
    """
    import re

    # Replace numeric IDs
    path = re.sub(r'/\d+', '/{id}', path)

    # Replace UUIDs (8-4-4-4-12 format)
    path = re.sub(
        r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
        '/{uuid}',
        path,
        flags=re.IGNORECASE
    )

    # Replace other hex IDs or alphanumeric IDs (common patterns)
    path = re.sub(r'/[a-zA-Z0-9_-]{16,}', '/{token}', path)

    # Limit endpoint length (truncate very long paths)
    if len(path) > 100:
        path = path[:97] + '...'

    return path


def monitor_function(metric_name: str = None):
    """
    Decorator to monitor function execution time and errors.

    Can be used to instrument specific functions beyond HTTP requests,
    such as background jobs, service methods, etc.

    Usage:
        @monitor_function('user_registration')
        def register_user(email, password):
            # ... implementation

    Args:
        metric_name: Optional name for the metric (defaults to function name)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            success = True
            error_type = None

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_type = type(e).__name__
                raise
            finally:
                duration = time.time() - start_time

                # Log slow operations
                if duration > 1.0:  # Threshold: 1 second
                    logger.warning(
                        f"Slow operation: {metric_name or func.__name__} "
                        f"took {duration:.2f}s"
                    )

        return wrapper
    return decorator
