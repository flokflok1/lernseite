"""
Admin AI Studio API Package

Flat structure matching 05_Backend-Struktur.md documentation.

Modules:
- ai_studio_actions.py: AI Studio authoring actions

Future modules:
- ai_studio.py: Studio main interface
- ai_studio_chat.py: Chat interface
- ai_studio_generation.py: Content generation
- ai_studio_sessions.py: Session management
- ai_studio_utils.py: Utilities
- ai_studio_variants.py: Variant management

All routes: /api/v1/admin/studio/*
"""

# Import route handlers and blueprints
from app.api.v1.admin.studio import ai_studio_actions

# Import blueprints for registration
from app.api.v1.admin.studio.ai_studio_actions import ai_studio_actions_bp

# Register blueprints with api_v1
from app.api.v1 import api_v1

api_v1.register_blueprint(ai_studio_actions_bp)

__all__ = [
    'ai_studio_actions',
    'ai_studio_actions_bp'
]
