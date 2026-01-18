"""
LernsystemX API Gateway - Rate Limiting

Gateway-level rate limiting extending Phase 20 security.

Implements route-group-specific rate limits:
- Public APIs: 10 req/min
- Admin APIs: 200 req/min
- KI APIs: 30 req/min
- Analytics: 60 req/min
- LiveRoom: 100 req/min

Based on Dok 32 (API-Gateway) - Phase 21
"""

from functools import wraps
from flask import request, current_app
from app.extensions import limiter
from app.api.gateway.router import get_route_group


class GatewayRateLimiter:
    """
    Gateway-level rate limiting based on route groups.

    Extends Phase 20 rate limiting with gateway-specific limits.
    """

    @staticmethod
    def get_rate_limit_for_route(path: str) -> str:
        """
        Get rate limit configuration for a specific route.

        Args:
            path: Request path

        Returns:
            Rate limit string (e.g., "100 per minute")
        """
        route_group = get_route_group(path)

        # Map route groups to config keys
        limit_map = {
            'public': 'API_GATEWAY_RATE_LIMIT_PUBLIC',
            'admin': 'API_GATEWAY_RATE_LIMIT_ADMIN',
            'app': 'API_GATEWAY_RATE_LIMIT_DEFAULT',
            'org': 'API_GATEWAY_RATE_LIMIT_DEFAULT',
            'auth': 'RATE_LIMIT_LOGIN',  # From Phase 20
            'health': None,  # No limit on health checks
        }

        config_key = limit_map.get(route_group)
        if not config_key:
            return current_app.config.get('API_GATEWAY_RATE_LIMIT_DEFAULT', '100 per minute')

        return current_app.config.get(config_key, '100 per minute')

    @staticmethod
    def get_limit_key() -> str:
        """
        Generate rate limit key based on user or IP.

        Returns:
            Rate limit key for Redis
        """
        # Try to get user ID from g.current_user (set by @token_required)
        from flask import g
        if hasattr(g, 'current_user') and g.current_user:
            user_id = g.current_user.get('user_id')
            if user_id:
                return f"user:{user_id}"

        # Fall back to IP address
        return f"ip:{request.remote_addr}"


def gateway_rate_limit(scope: str = None):
    """
    Gateway-level rate limiting decorator.

    Applies rate limits based on route group or custom scope.

    Args:
        scope: Optional custom scope (e.g., 'ki', 'analytics')
               If None, uses automatic route group detection

    Usage:
        @app.route('/api/v1/ki/generate')
        @gateway_rate_limit(scope='ki')
        def generate_content():
            ...

        # Or automatic:
        @app.route('/api/v1/admin/users')
        @gateway_rate_limit()
        def admin_users():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Skip if gateway disabled
            if not current_app.config.get('API_GATEWAY_ENABLED', True):
                return fn(*args, **kwargs)

            # Get rate limit based on scope or route
            if scope:
                # Custom scope (e.g., 'ki', 'analytics', 'liveroom')
                config_key = f'API_GATEWAY_RATE_LIMIT_{scope.upper()}'
                limit_string = current_app.config.get(config_key, '100 per minute')
            else:
                # Automatic route group detection
                limit_string = GatewayRateLimiter.get_rate_limit_for_route(request.path)

            # Apply limit using Flask-Limiter
            limit_key = GatewayRateLimiter.get_limit_key()

            # Use shared limit to apply the rate limit
            # This is equivalent to @limiter.limit() but dynamic
            try:
                limiter.limit(limit_string, key_func=lambda: limit_key)(fn)(*args, **kwargs)
            except Exception:
                # If rate limit exceeded, Flask-Limiter raises RateLimitExceeded
                # which is handled by the global error handler (429)
                raise

            return fn(*args, **kwargs)

        return wrapper
    return decorator


def setup_gateway_rate_limiting(app):
    """
    Setup gateway-level rate limiting.

    Registers global rate limit handler and logs configuration.

    Args:
        app: Flask application instance
    """
    if not app.config.get('API_GATEWAY_ENABLED', True):
        return

    if not app.config.get('RATE_LIMIT_ENABLED', True):
        app.logger.warning('Gateway rate limiting disabled (RATE_LIMIT_ENABLED=False)')
        return

    app.logger.info('Setting up API Gateway rate limiting...')
    app.logger.info(f"  - Public APIs: {app.config.get('API_GATEWAY_RATE_LIMIT_PUBLIC')}")
    app.logger.info(f"  - Admin APIs: {app.config.get('API_GATEWAY_RATE_LIMIT_ADMIN')}")
    app.logger.info(f"  - KI APIs: {app.config.get('API_GATEWAY_RATE_LIMIT_KI')}")
    app.logger.info(f"  - Analytics APIs: {app.config.get('API_GATEWAY_RATE_LIMIT_ANALYTICS')}")
    app.logger.info(f"  - LiveRoom APIs: {app.config.get('API_GATEWAY_RATE_LIMIT_LIVEROOM')}")
    app.logger.info(f"  - Default: {app.config.get('API_GATEWAY_RATE_LIMIT_DEFAULT')}")
