"""
AI Editor API Package

Chat-based AI-powered course authoring with quick actions.

Modules:
- authoring.py: AI-powered chat-based authoring with sessions
- actions.py: Quick actions for content generation

All routes: /api/v1/course-editor/ai/*
"""

from flask import Blueprint

# Create ai_editor blueprint
ai_editor_bp = Blueprint('ai_editor', __name__, url_prefix='/ai')

# Import route modules (they will register their routes on ai_editor_bp)
from app.api.v1.course_editor.ai_editor import authoring, actions

# Register sub-blueprints
ai_editor_bp.register_blueprint(actions.actions_bp)

__all__ = ['ai_editor_bp']
