"""
LernsystemX Tokens Admin Package

Admin-only token management endpoints.

Endpoints:
- POST /api/v1/tokens/manual-topup - Manual token top-up
- GET /api/v1/tokens/stats - Get global token statistics
"""

from .management import tokens_admin_bp

__all__ = ['tokens_admin_bp']
