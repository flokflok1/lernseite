"""Backward Compatibility Bridge: permission_service
DEPRECATED: Use 'from app.services.system.auth.permission import PermissionService' instead
This bridge maintains backward compatibility with old import paths.
"""
from app.services.system.auth.permission import PermissionService
__all__ = ['PermissionService']
