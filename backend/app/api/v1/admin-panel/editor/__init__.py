"""
Admin AI Editor API Package

Flat structure matching 05_Backend-Struktur.md documentation.

Modules:
- ai_editor_actions.py: AI Editor authoring actions

Future modules:
- ai_editor.py: Editor main interface
- ai_editor_chat.py: Chat interface
- ai_editor_generation.py: Content generation
- ai_editor_sessions.py: Session management
- ai_editor_utils.py: Utilities
- ai_editor_variants.py: Variant management

All routes: /api/v1/admin/ai-editor/*
"""

# Import route handlers and blueprints
from .editor import ai_editor_actions

# Import blueprints for registration
from .editor.ai_editor_actions import ai_editor_actions_bp

# Register blueprints with api_v1
from app.api.v1 import api_v1

api_v1.register_blueprint(ai_editor_actions_bp)

__all__ = [
    'ai_editor_actions',
    'ai_editor_actions_bp'
]
