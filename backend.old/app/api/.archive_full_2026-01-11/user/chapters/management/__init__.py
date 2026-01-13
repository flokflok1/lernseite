"""
LernsystemX Chapter Theory Management Package

CRUD operations split for maintainability:
- list_get: List and get operations (read-only)
- update_delete: Update and delete operations (write)

Structure:
    list_get.py      ~210 lines  - /chapters/<id>/theories, /chapters/<id>/theory
    update_delete.py ~129 lines  - /chapter-theory/<id> PATCH/DELETE

Refactored from chapter_theory/crud.py (339 lines) - 2026-01-08
Per Developer-Guide-KI Section 10.2 (Max 500 lines per file)
"""

from .list_get import chapter_theory_list_get_bp
from .update_delete import chapter_theory_update_delete_bp

__all__ = [
    'chapter_theory_list_get_bp',
    'chapter_theory_update_delete_bp',
]
