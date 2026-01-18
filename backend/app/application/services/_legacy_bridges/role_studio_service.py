"""Backward Compatibility Bridge: role_studio_service
DEPRECATED: Use 'from app.application.services.system.auth.studio import RoleStudioService' instead
This bridge maintains backward compatibility with old import paths.
"""
from app.application.services.system.auth.studio import RoleStudioService
__all__ = ['RoleStudioService']
