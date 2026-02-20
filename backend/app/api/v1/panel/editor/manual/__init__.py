"""
Manual Editor API Package

Traditional CRUD editor for courses without AI.

Modules:
- courses.py: Course CRUD operations
- chapters.py: Chapter CRUD operations
- lessons.py: Lesson CRUD operations
- exams.py: Exam CRUD operations
- theory_sheets.py: Theory sheet CRUD operations
- course_files.py: File attachment management
- course_prompts.py: Prompt override management

All routes: /api/v1/course-editor/manual/*

Moved from: api/v1/course_editor/manual_editor/ → api/v1/courses/editor/manual/
Part of: Phase 3 Courses Consolidation
"""

from flask import Blueprint

# Create manual_editor blueprint
manual_editor_bp = Blueprint('manual_editor', __name__, url_prefix='/manual')

# Import route modules (they will register their routes on manual_editor_bp)
from . import (
    courses,
    chapters,
    lessons,
    lesson_activities,
    exams,
    theory_sheets,
    course_files,
    course_prompts
)

__all__ = ['manual_editor_bp']
