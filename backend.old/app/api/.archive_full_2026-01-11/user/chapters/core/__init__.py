"""
LernsystemX Chapter Theory Core Package

Core domain logic for chapter theories.

Modules:
    - repository: Database access layer
    - factory: DDD Factory Pattern for theory creation

DDD Refactored: 2026-01-08
Per Developer-Guide-KI DDD Pattern
"""

from .repository import (
    get_chapter_theory,
    get_chapter_theory_by_id,
    list_chapter_theories,
    save_chapter_theory,
    update_chapter_theory_title,
    delete_chapter_theory_by_id,
    delete_chapter_theory_by_style,
    get_chapter_info,
    get_chapter_lessons,
    get_fallback_theory,
)
from .factory import TheoryFactory

__all__ = [
    # Repository
    'get_chapter_theory',
    'get_chapter_theory_by_id',
    'list_chapter_theories',
    'save_chapter_theory',
    'update_chapter_theory_title',
    'delete_chapter_theory_by_id',
    'delete_chapter_theory_by_style',
    'get_chapter_info',
    'get_chapter_lessons',
    'get_fallback_theory',
    # Factory
    'TheoryFactory',
]
