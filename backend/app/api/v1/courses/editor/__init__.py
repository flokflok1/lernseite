"""
Courses Editor Module

Course editor endpoints (AI editor, manual editor, shared services).

Structure:
- ai/: AI course authoring
- manual/: Manual course editing
- shared/: Shared editor services

Moved from: api/v1/course_editor/ → api/v1/courses/editor/
Part of: Phase 3 Courses Consolidation
"""

from flask import Blueprint

# Create course_editor parent blueprint
course_editor_bp = Blueprint('course_editor', __name__, url_prefix='/course-editor')

# Import sub-blueprints
from app.api.v1.courses.editor.ai import ai_editor_bp
from app.api.v1.courses.editor.manual import manual_editor_bp

# Register sub-blueprints
course_editor_bp.register_blueprint(ai_editor_bp)
course_editor_bp.register_blueprint(manual_editor_bp)

__all__ = ['course_editor_bp', 'ai_editor_bp', 'manual_editor_bp']
