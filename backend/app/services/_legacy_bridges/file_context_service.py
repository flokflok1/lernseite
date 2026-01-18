"""Backward Compatibility Bridge: file_context_service
DEPRECATED: Use 'from app.services.system.files import FileContextService' instead
This bridge maintains backward compatibility with old import paths.
"""
from app.services.system.files import FileContextService
__all__ = ['FileContextService']
