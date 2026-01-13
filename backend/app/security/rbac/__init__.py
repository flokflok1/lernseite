"""
Role-Based Access Control (RBAC) Module

This module provides decorators and utilities for access control.
Currently implements Owner-Admin system.
"""

from app.security.rbac.decorators import (
    require_owner,
    require_owner_or_permission
)

__all__ = [
    'require_owner',
    'require_owner_or_permission'
]
