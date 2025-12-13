"""
LernsystemX API Package

RESTful API endpoints for LernsystemX:
- Authentication (login, register, JWT, 2FA)
- User management (CRUD, profile)
- Course management
- Organisation management
- Learning methods
- Subscriptions and billing
- Token management

Uses:
- Flask Blueprints for modular routing
- Pydantic for request/response validation
- JWT for authentication
- RBAC for authorization

ISO/IEC/IEEE 26515:2018 compliant - API documentation
"""

from flask import Blueprint

# Create API blueprint (version 1)
api_v1 = Blueprint(
    'api_v1',
    __name__,
    url_prefix='/api/v1'
)

# Import routes after blueprint creation to avoid circular imports
from app.api import auth
from app.api import users
from app.api import profile
from app.api import courses
from app.api import categories
from app.api import learning_methods
from app.api import subscriptions
from app.api import tokens
from app.api import organisations
from app.api import dashboard
from app.api import analytics
from app.api import admin_analytics
from app.api import admin_system  # Phase 22: System version endpoints
from app.api import admin_users  # Phase B24: Admin user management
from app.api import admin_courses  # Phase B24-02: Admin course management
from app.api import admin_learning_methods  # Phase D3.2: Admin learning methods (32 Methoden, LM00-LM31)
# Phase D4: KI-Authoring-Studio (modular split per 35_Developer-Guide-KI-Prompts.md)
from app.api import admin_ai_studio  # Main facade - imports all sub-modules
from app.api import admin_ai_studio_sessions  # Session CRUD
from app.api import admin_ai_studio_generation  # Source, generation, PDF, templates
from app.api import admin_ai_studio_variants  # Variants and snapshots
from app.api import admin_ai_studio_chat  # Chat interface, LM generation
# Note: admin_ai_studio_utils.py contains helper functions only (no routes)
from app.api import admin_ai_tutor  # Phase KI-Studio: Tutor content generation (chapter theory, lesson steps)
from app.api import admin_prompts  # Phase KI-Studio: Prompt template management (CRUD, styles, TTS)
from app.api import admin_ai_models  # Phase KI-Architektur: AI Model Management (sync, update, pricing)
from app.api import admin_lm_routing  # Phase KI-Architektur: LM Model Routing (Lernmethoden -> Modelle)
from app.api import tutor  # Global 3D AI Tutor Companion
from app.api import audio  # Audio STT/TTS and realtime audio processing
from app.api import tts  # TTS API with caching for Tutor Avatar
from app.api import org_analytics
from app.api import agents  # Smart Agent System - Course agents with caching
from app.api import feedback  # Feedback System with AI summaries
from app.api import lesson_videos  # Lesson Video Generation with Sora 2 + TTS-1-HD
from app.api import chapter_theory  # User-facing chapter theory with Whiteboard

__all__ = ['api_v1']
