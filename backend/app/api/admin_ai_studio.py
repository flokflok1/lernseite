"""
LernsystemX Admin AI Studio API

KI-Authoring-Studio endpoints for AI-powered chapter creation.
This module serves as the main entry point and imports all sub-modules.

Endpoints are organized in separate modules:
- admin_ai_studio_sessions.py   - Session CRUD operations
- admin_ai_studio_generation.py - Source data, generation, finalize, PDF upload, templates
- admin_ai_studio_variants.py   - Variants and snapshots management
- admin_ai_studio_chat.py       - Chat interface and LM content generation
- admin_ai_studio_utils.py      - Helper functions

API Endpoints:
Session Management:
- GET    /api/v1/admin/ai-studio/sessions         - List user's sessions
- POST   /api/v1/admin/ai-studio/sessions         - Create new session
- GET    /api/v1/admin/ai-studio/sessions/{id}    - Get session details
- PATCH  /api/v1/admin/ai-studio/sessions/{id}    - Update session
- DELETE /api/v1/admin/ai-studio/sessions/{id}    - Delete session

Source & Generation:
- POST   /api/v1/admin/ai-studio/sessions/{id}/source    - Set source data
- POST   /api/v1/admin/ai-studio/sessions/{id}/generate  - Generate content
- POST   /api/v1/admin/ai-studio/sessions/{id}/finalize  - Finalize and create chapter
- POST   /api/v1/admin/ai-studio/upload-pdf              - Upload and analyze PDF
- GET    /api/v1/admin/ai-studio/templates               - Get available templates
- GET    /api/v1/admin/ai-studio/stats                   - Get user stats

Variants & Snapshots:
- GET    /api/v1/admin/ai-studio/sessions/{id}/variants              - Get variants
- POST   /api/v1/admin/ai-studio/sessions/{id}/variants/select       - Select variant
- POST   /api/v1/admin/ai-studio/sessions/{id}/variants/rate         - Rate variant
- GET    /api/v1/admin/ai-studio/sessions/{id}/snapshots             - Get snapshots
- POST   /api/v1/admin/ai-studio/sessions/{id}/snapshots             - Create snapshot
- POST   /api/v1/admin/ai-studio/sessions/{id}/snapshots/{snap_id}/restore - Restore

Chat & LM Generation:
- POST   /api/v1/admin/ai-studio/chat        - Chat with AI for content creation
- POST   /api/v1/admin/ai-studio/generate-lm - Generate learning method content

Phase D4 - KI-Authoring-Studio - ISO 27001:2013 compliant
Module split according to 35_Developer-Guide-KI-Prompts.md guidelines

Version: 2.0
Last Updated: 2025-01
"""

# Import all sub-modules to register their routes with the blueprint
# The routes are automatically registered when Flask imports these modules

from app.api import admin_ai_studio_sessions      # Session CRUD
from app.api import admin_ai_studio_generation    # Source, generation, PDF, templates
from app.api import admin_ai_studio_variants      # Variants and snapshots
from app.api import admin_ai_studio_chat          # Chat interface, LM generation

# Note: admin_ai_studio_utils.py contains only helper functions (no routes)
# and is imported by admin_ai_studio_chat.py

# Tutor endpoints (generate-chapter-theory, generate-lesson-steps)
# are in admin_ai_tutor.py (separate module)

__all__ = [
    'admin_ai_studio_sessions',
    'admin_ai_studio_generation',
    'admin_ai_studio_variants',
    'admin_ai_studio_chat'
]
