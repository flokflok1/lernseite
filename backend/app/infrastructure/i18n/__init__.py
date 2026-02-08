"""
LernsystemX i18n Infrastructure Package
========================================

Non-blueprint infrastructure for internationalization:
    - error_codes.py           - ErrorCode enum (used by 40+ files)
    - error_code_i18n_mapping.py - Error-to-i18n mapping
    - message_codes.py         - Message code definitions
    - _helpers.py              - Internal helpers

Blueprint registration has been moved to app.api.v1.i18n (DDD layer rule).
"""

# Keep non-blueprint exports accessible
# error_codes is imported by 40+ files across the codebase via:
#   from app.infrastructure.i18n.error_codes import ErrorCode

__all__: list[str] = []
