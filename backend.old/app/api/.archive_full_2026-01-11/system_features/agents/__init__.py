"""
LernsystemX Smart Agent API Package

Course agent endpoints for intelligent Q&A, voice interaction, and knowledge management.
Refactored from flat structure into 5 focused packages.

Packages:
    - core: Ask, status, config endpoints (~219 lines)
    - knowledge: Feedback, knowledge CRUD, cache warming (~222 lines)
    - admin: Admin-only agent listing and statistics (~83 lines)
    - audio: TTS and voice-to-voice endpoints (~171 lines)
    - media: Media cache stats and serving (~100 lines)

Structure (all under 500 lines):
    _helpers.py          ~102 lines   - Shared helper functions
    core/engine.py       ~219 lines   - /agents/<id>/ask, /status, /config
    knowledge/base.py    ~222 lines   - /agents/<id>/feedback, /knowledge, /cache, /warm
    admin/management.py   ~83 lines   - /admin/agents, /admin/agents/<id>/stats
    audio/processing.py  ~171 lines   - /agents/<id>/ask/audio, /ask/voice
    media/handling.py    ~100 lines   - /agents/<id>/media/stats, /media/tts/<id>

Route Registration:
    All routes are registered on api_v1 blueprint via nested blueprint pattern.
    When this package is imported, blueprints are auto-registered on api_v1.

Endpoints:
    POST   /api/v1/agents/:course_id/ask          - Ask the agent a question (text)
    POST   /api/v1/agents/:course_id/ask/audio    - Ask with TTS audio response
    POST   /api/v1/agents/:course_id/ask/voice    - Ask via voice (transcribe + respond + TTS)
    GET    /api/v1/agents/:course_id/status       - Get agent status
    GET    /api/v1/agents/:course_id/config       - Get agent configuration
    PUT    /api/v1/agents/:course_id/config       - Update agent config (admin)
    POST   /api/v1/agents/:course_id/feedback     - Submit feedback
    POST   /api/v1/agents/:course_id/knowledge    - Add knowledge entry (admin)
    DELETE /api/v1/agents/:course_id/cache        - Invalidate cache (admin)
    POST   /api/v1/agents/:course_id/warm         - Warm up agent cache (admin)
    GET    /api/v1/agents/:course_id/media/stats  - Get media cache statistics
    GET    /api/v1/admin/agents                   - List all agents (admin)
    GET    /api/v1/admin/agents/:agent_id/stats   - Get agent statistics (admin)
    GET    /api/v1/media/tts/:media_id            - Serve cached TTS audio

ISO 9001:2015 compliant - Agent API Package
Refactored: 2026-01-08 per Developer-Guide-KI Section 10
"""

from .core import agents_core_bp
from .knowledge import agents_knowledge_bp
from .admin import agents_admin_bp
from .audio import agents_audio_bp
from .media import agents_media_bp, media_bp

# All blueprints in this package
ALL_BLUEPRINTS = [
    agents_core_bp,
    agents_knowledge_bp,
    agents_admin_bp,
    agents_audio_bp,
    agents_media_bp,
    media_bp,
]

# Register all sub-blueprints on api_v1 (nested blueprint pattern)
# This is executed when the package is imported from app/api/__init__.py
from app.api import api_v1

for bp in ALL_BLUEPRINTS:
    api_v1.register_blueprint(bp)


# Export all blueprints for direct import
__all__ = [
    'agents_core_bp',
    'agents_knowledge_bp',
    'agents_admin_bp',
    'agents_audio_bp',
    'agents_media_bp',
    'media_bp',
    'ALL_BLUEPRINTS',
]
