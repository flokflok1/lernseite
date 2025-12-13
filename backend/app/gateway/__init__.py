"""
LernsystemX API Gateway Module

Centralized API Gateway for LernsystemX implementing:
- Request routing and segmentation
- Gateway-level rate limiting
- Request tracking and analytics
- Multi-tenant domain routing
- API versioning and deprecation management

Based on:
- Dok 32 (API-Gateway) - Phase 21
- Dok 33 (Versioning-Change-Management) - Phase 22

ISO 27001:2013 compliant - Access Control
"""

from .router import register_gateway_routes
from .middleware import setup_gateway_middleware
from .rate_limiting import gateway_rate_limit, GatewayRateLimiter
from .analytics import GatewayAnalytics
from .versioning import setup_gateway_versioning, get_api_version, get_version_info

__all__ = [
    'register_gateway_routes',
    'setup_gateway_middleware',
    'gateway_rate_limit',
    'GatewayRateLimiter',
    'GatewayAnalytics',
    'setup_gateway_versioning',
    'get_api_version',
    'get_version_info',
]
