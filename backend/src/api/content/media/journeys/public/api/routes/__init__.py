"""
Media Domain - Public Journey Routes

Public information routes for media capabilities.

Routes:
- info.py: supported-formats, voices (2 endpoints)

Total: 2 public endpoints
"""

from .info import media_info_bp

__all__ = [
    'media_info_bp',
]
