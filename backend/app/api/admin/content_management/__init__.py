"""
Admin Content Management

Content-Admin für Kurse, Lektionen, Kapitel, Exams.

Struktur:
- courses/ - Course CRUD, Files, Prompts
- analytics/ - Course Analytics
- (TODO: chapters/, lessons/, categories/, learning-methods/)

Migration Status: IN PROGRESS
"""

# Import from content-management submodules
from app.api.admin.content_management.courses import (
    crud as courses_crud,
    chapters,
    lessons,
    exams,
    prompts,
    files
)

__all__ = [
    'courses_crud',
    'chapters',
    'lessons',
    'exams',
    'prompts',
    'files'
]
