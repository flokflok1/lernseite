"""Panel Editor API — Course editor endpoints."""

from flask import Blueprint

from .ai import ai_editor_bp
from .manual import manual_editor_bp

course_editor_bp = Blueprint('course_editor', __name__, url_prefix='/course-editor')
course_editor_bp.register_blueprint(ai_editor_bp)
course_editor_bp.register_blueprint(manual_editor_bp)

__all__ = ['course_editor_bp']
