"""
File Context Service Bridge - LEGACY IMPORT PATH

NOTICE: This file exists for backward compatibility only.
The actual implementation has been moved to app/services/system/files/context.py

DEPRECATED IMPORT (old path - still works):
    from app.services.file_context_service import FileContextService

RECOMMENDED IMPORT (new path):
    from app.services.system.files import FileContextService

This bridge re-exports the FileContextService class for backward compatibility
with existing code. All new code should use the recommended import path.
"""

# Re-export from the actual location for backward compatibility
from app.services.system.files import FileContextService

__all__ = ['FileContextService']
