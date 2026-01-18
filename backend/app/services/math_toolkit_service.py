"""
Math Toolkit Service Bridge - LEGACY IMPORT PATH

NOTICE: This file exists for backward compatibility only.
The actual implementation has been moved to app/services/math_toolkit/ package.

DEPRECATED IMPORT (old path - still works):
    from app.services.math_toolkit_service import MathToolkitService

RECOMMENDED IMPORT (new path):
    from app.services.math_toolkit import MathToolkitService

This bridge re-exports the MathToolkitService class for backward compatibility
with existing code. All new code should use the recommended import path.
"""

# Re-export from the actual location for backward compatibility
from app.services.math_toolkit import MathToolkitService

__all__ = ['MathToolkitService']
