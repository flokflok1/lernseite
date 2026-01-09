"""
Admin Assessment Management

Prüfungsverwaltung (Exams, Results).

Struktur:
- exams/ - Exam CRUD, Questions, Results

Migration Status: TODO
"""

# TODO: Import exam blueprints from content-management/courses/exams
# Temporär: Import from old location
from app.api.admin.content_management.courses import exams

__all__ = ['exams']
