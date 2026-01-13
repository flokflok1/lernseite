"""
Admin Assessment Management

Prüfungsverwaltung (Exams, Results).

Struktur:
- exams/ - Exam CRUD, Questions, Results

Migration Status: DONE - Migrated to v1/admin/courses/
"""

# Import from new flat structure
from app.api.v1.admin.courses import exams

__all__ = ['exams']
