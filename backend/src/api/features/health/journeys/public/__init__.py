"""
Health Domain - Public Journey

Public health check journeys for monitoring.

Routes:
- Basic health check
- Detailed health check

Architecture: Journey-Based (Public Utility)
"""

from .api.routes import health_check, health_check_detailed

__all__ = ['health_check', 'health_check_detailed']
