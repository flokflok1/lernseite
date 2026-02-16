"""
LernsystemX Middleware Package

Middleware for request/response processing:
- Authentication (JWT verification)
- Authorization (RBAC)
- Rate limiting
- Request logging
- Error handling
- Monitoring & Metrics

ISO 27001:2013 compliant - Access control
"""

from app.api.middleware.auth import (
    token_required,
    admin_required,
    role_required,
    get_current_user,
    get_current_user_id
)

from app.api.middleware.monitoring_middleware import (
    setup_monitoring_middleware,
    monitor_function
)

__all__ = [
    'token_required',
    'admin_required',
    'role_required',
    'get_current_user',
    'get_current_user_id',
    'setup_monitoring_middleware',
    'monitor_function',
]
