"""
Authentication & Authorization Services

Permission and role management:
- Permission checking and enforcement
- Role definition and hierarchy
"""

from .permission import PermissionService

__all__ = [
    'PermissionService',
]
