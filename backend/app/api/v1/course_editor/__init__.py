"""
Course Editor API Package

Feature-based course editor with Manual Editor and AI Editor.

Modules:
- shared: Shared permission decorators and utilities
- manual_editor: Manual CRUD editor for courses
- ai_editor: AI-powered chat-based authoring

All routes: /api/v1/course-editor/*
"""

from flask import Blueprint

# Create course_editor blueprint
course_editor_bp = Blueprint('course_editor', __name__, url_prefix='/course-editor')

# Import sub-modules (will register their routes)
from app.api.v1.course_editor.manual_editor import manual_editor_bp
from app.api.v1.course_editor.ai_editor import ai_editor_bp

# Register sub-blueprints
course_editor_bp.register_blueprint(manual_editor_bp)
course_editor_bp.register_blueprint(ai_editor_bp)

__all__ = ['course_editor_bp', 'manual_editor_bp', 'ai_editor_bp']
