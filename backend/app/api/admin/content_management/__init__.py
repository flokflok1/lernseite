"""
Admin Content Management

Content-Admin für Kurse, Lektionen, Kapitel, Exams.

Struktur:
- courses/ - Course CRUD, Files, Prompts, Authoring (Kurs Studio)
- analytics/ - Course Analytics
- (TODO: chapters/, lessons/, categories/, learning-methods/)

Migration Status: IN PROGRESS
"""

# Import courses package to trigger blueprint registration
# Note: courses/__init__.py handles all submodule imports and blueprint registration
from app.api.admin.content_management import courses

__all__ = ['courses']
