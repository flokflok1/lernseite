"""
Admin Content Management

Content-Admin für Kurse, Lektionen, Kapitel, Exams, Plugins.

Struktur:
- courses/ - Course CRUD, Files, Prompts, Authoring (Kurs Studio)
- analytics/ - Course Analytics
- plugins.py - Learning Methods Plugin System (8 endpoints)
- (TODO: chapters/, lessons/, categories/, learning-methods/)

Migration Status: IN PROGRESS
"""

# Import courses package to trigger blueprint registration
# Note: courses/__init__.py handles all submodule imports and blueprint registration
from app.api.admin.content_management import courses

# Import plugins module to register routes on api_v1
from app.api.admin.content_management import plugins

__all__ = ['courses', 'plugins']
