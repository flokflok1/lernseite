"""
LernsystemX API Gateway - Analytics & Logging

Gateway-level request tracking and analytics.

Tracks:
- Request count per route group
- Response times
- Status codes
- User/IP distribution
- Route group usage

Integrates with Phase 19 Monitoring (Prometheus).

Based on Dok 32 (API-Gateway) - Phase 21
"""

from flask import Flask, request, g
from datetime import datetime
import uuid
from typing import Optional
from app.gateway.router import get_route_group


class GatewayAnalytics:
    """
    Gateway analytics and request tracking.

    Collects metrics for monitoring and analysis without storing sensitive data.
    """

    def __init__(self, app: Flask = None):
        """Initialize gateway analytics"""
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """
        Initialize analytics with Flask app.

        Registers before_request and after_request handlers.

        Args:
            app: Flask application instance
        """
        self.app = app

        if not app.config.get('API_GATEWAY_ENABLED', True):
            return

        if not app.config.get('API_GATEWAY_TRACK_ANALYTICS', True):
            app.logger.info('Gateway analytics disabled')
            return

        # Register request tracking
        app.before_request(self.before_request)
        app.after_request(self.after_request)

        app.logger.info('Gateway analytics initialized')

    def before_request(self):
        """
        Track request start time and generate request ID.

        Executed before each request.
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        g.gateway_request_id = request_id
        g.gateway_start_time = datetime.utcnow()

        # Determine route group
        g.gateway_route_group = get_route_group(request.path)

        # Add request ID to response headers later
        return None

    def after_request(self, response):
        """
        Track request completion and log analytics.

        Args:
            response: Flask response object

        Returns:
            Modified response with tracking headers
        """
        if not self.app.config.get('API_GATEWAY_TRACK_ANALYTICS', True):
            return response

        # Calculate request duration
        if hasattr(g, 'gateway_start_time'):
            duration = (datetime.utcnow() - g.gateway_start_time).total_seconds()
        else:
            duration = 0

        # Add request ID header
        request_id_header = self.app.config.get('API_GATEWAY_REQUEST_ID_HEADER', 'X-LSX-Request-ID')
        if hasattr(g, 'gateway_request_id'):
            response.headers[request_id_header] = g.gateway_request_id

        # Add API version header
        response.headers['X-LSX-API-Version'] = self.app.config.get('API_VERSION', '1')

        # Add route group header (for debugging/monitoring)
        if hasattr(g, 'gateway_route_group') and self.app.config.get('DEBUG', False):
            response.headers['X-LSX-Route-Group'] = g.gateway_route_group

        # Log analytics if enabled
        if self.app.config.get('API_GATEWAY_LOG_REQUESTS', True):
            self._log_request_analytics(response, duration)

        # Track Prometheus metrics if monitoring enabled
        if self.app.config.get('MONITORING_ENABLED', False):
            self._track_prometheus_metrics(response, duration)

        return response

    def _log_request_analytics(self, response, duration: float):
        """
        Log request analytics to application logs.

        Args:
            response: Flask response object
            duration: Request duration in seconds
        """
        route_group = getattr(g, 'gateway_route_group', 'unknown')
        request_id = getattr(g, 'gateway_request_id', 'n/a')

        # Get user info if authenticated
        user_id = None
        org_id = None
        if hasattr(g, 'current_user') and g.current_user:
            user_id = g.current_user.get('user_id')
            org_id = g.current_user.get('organization_id')

        # Build log message (no sensitive data)
        log_data = {
            'request_id': request_id,
            'route_group': route_group,
            'method': request.method,
            'path': request.path,
            'status': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'user_id': user_id,
            'org_id': org_id,
            'ip': request.remote_addr,
        }

        # Log as JSON-friendly string
        self.app.logger.info(f"Gateway: {log_data}")

    def _track_prometheus_metrics(self, response, duration: float):
        """
        Track request metrics in Prometheus.

        Args:
            response: Flask response object
            duration: Request duration in seconds
        """
        try:
            from app.monitoring import (
                http_requests_total,
                http_request_duration_seconds,
            )

            route_group = getattr(g, 'gateway_route_group', 'unknown')

            # Track request count
            http_requests_total.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown',
                status=response.status_code,
                route_group=route_group
            ).inc()

            # Track request duration
            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown',
                route_group=route_group
            ).observe(duration)

        except ImportError:
            # Monitoring not configured
            pass
        except Exception as e:
            # Don't break request flow on metrics errors
            self.app.logger.error(f"Failed to track Prometheus metrics: {str(e)}")


# Global instance
_gateway_analytics = GatewayAnalytics()


def setup_gateway_analytics(app: Flask):
    """
    Setup gateway analytics for the application.

    Args:
        app: Flask application instance
    """
    _gateway_analytics.init_app(app)
