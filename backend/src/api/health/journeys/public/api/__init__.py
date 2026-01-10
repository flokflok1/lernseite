"""
Health Domain - Public Journey API Layer

API routes for health monitoring.
"""

from .routes import health_check, health_check_detailed

__all__ = ['health_check', 'health_check_detailed']
