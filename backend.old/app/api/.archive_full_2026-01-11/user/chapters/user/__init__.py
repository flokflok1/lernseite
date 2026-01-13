"""
LernsystemX Chapter Theory User Package

User-facing read-only operations for chapter theories.

Modules:
    - read: List and get operations for end-users

DDD Refactored: 2026-01-08
Per Developer-Guide-KI DDD Pattern and ISO/IEC 26515
"""

from .read import chapter_theory_user_read_bp

__all__ = [
    'chapter_theory_user_read_bp',
]
