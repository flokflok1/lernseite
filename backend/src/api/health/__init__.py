"""Health Domain - System Health Checks

Minimalistic domain (no entities/repositories needed).
Only provides health check endpoints for monitoring.

Handles:
- Basic health check (/health)
- Detailed health check (/health/detailed)
- Database connectivity check
- Redis connectivity check
- Application uptime

Journeys:
- Public: health_check, health_check_detailed
"""
from src.api.health.journeys import ALL_HEALTH_ROUTES, health_check, health_check_detailed

__all__ = [
    'ALL_HEALTH_ROUTES',
    'health_check',
    'health_check_detailed',
]
