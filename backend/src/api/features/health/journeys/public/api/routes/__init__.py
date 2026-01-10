"""
Health Domain - Public Journey Routes

Utility endpoints for monitoring and load balancing.

Routes:
- GET /health - Basic health check
- GET /health/detailed - Detailed health check with component status

Architecture: Journey-Based (Public Utility)
Pattern: Simple utility routes (no DDD needed)
"""

# Import health check functions from health.py
from .health import health_check, health_check_detailed

# No blueprints needed - health routes are registered differently
# They're standalone functions called directly by the API Gateway

__all__ = [
    'health_check',
    'health_check_detailed',
]
