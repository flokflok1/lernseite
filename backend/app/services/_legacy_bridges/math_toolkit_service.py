"""Backward Compatibility Bridge: math_toolkit_service
DEPRECATED: Use 'from app.services.lm.math_toolkit import MathToolkitService' instead
This bridge maintains backward compatibility with old import paths.
"""
from app.services.lm.math_toolkit import MathToolkitService
__all__ = ['MathToolkitService']
