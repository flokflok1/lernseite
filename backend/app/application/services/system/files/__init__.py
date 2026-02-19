"""
File Management Services

File context and operations:
- File context detection and resolution (context.py)
- Multi-file context, AI formatting, preview, validation (context_part2.py)
- File metadata management
"""

from .context import FileContextService

# Attach extended methods (get_file_context, extract_for_ai_context,
# get_file_preview, validate_file) onto FileContextService
from . import context_part2  # noqa: F401

__all__ = [
    'FileContextService',
]
