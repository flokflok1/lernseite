"""
LernsystemX Agents Admin Package

Admin-only agent management endpoints.

Endpoints:
- GET /api/v1/admin/agents - List all agents
- GET /api/v1/admin/agents/:agent_id/stats - Get agent statistics
"""

from .management import agents_admin_bp

__all__ = ['agents_admin_bp']
