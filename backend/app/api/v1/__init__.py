"""
LernsystemX API v1 Package

Complete FLAT structure - all endpoints as single files per documentation.

Structure:
├── v1/
│   ├── auth.py              # Authentication (FLAT)
│   ├── users.py             # User management (FLAT)
│   ├── users_part2.py       # User management pt2 (FLAT)
│   ├── profile.py           # User profiles (FLAT)
│   ├── courses.py           # Courses (FLAT)
│   ├── categories.py        # Categories (FLAT)
│   ├── learning_methods.py  # Learning methods (FLAT)
│   ├── subscriptions.py     # Subscriptions (FLAT)
│   ├── tokens.py            # Tokens (FLAT)
│   ├── organisations.py     # Organisations (FLAT)
│   ├── feedback.py          # Feedback (FLAT)
│   ├── chapter_theory.py    # Chapter theory (FLAT)
│   ├── lesson_explanations.py # Lesson explanations (FLAT)
│   ├── lesson_videos.py     # Lesson videos (FLAT)
│   ├── exam_simulations.py  # Exam simulations (FLAT)
│   ├── tutor.py             # AI Tutor (FLAT)
│   ├── agents.py            # Smart agents (FLAT)
│   ├── audio.py             # Audio (FLAT)
│   ├── tts_core.py          # TTS core config & helpers (FLAT)
│   ├── tts_synthesis.py     # TTS synthesis endpoints (FLAT)
│   ├── tts_pronunciations.py # TTS pronunciation rules (FLAT)
│   ├── math_toolkit_practice.py # Math toolkit practice/sessions (FLAT)
│   ├── math_toolkit_reference.py # Math toolkit reference library (FLAT)
│   ├── math_toolkit_tasks.py # Math toolkit tasks/validation (FLAT)
│   ├── math_toolkit_admin.py # Math toolkit admin functions (FLAT)
│   ├── analytics.py         # Analytics (FLAT)
│   ├── org_analytics.py     # Org analytics (FLAT)
│   ├── health.py            # Health checks (FLAT)
│   ├── deprecation.py       # Deprecation (FLAT)
│   ├── /course_editor/      # Course Editor (FOLDER - feature-based)
│   ├── /dashboard/          # Dashboard (FOLDER - complex)
│   ├── /admin-panel/        # Admin Panel (FOLDER - complex)
│   ├── /social/             # Social (FOLDER - feature flagged)
│   ├── /community/          # Community (FOLDER - feature flagged)
│   └── /messaging/          # Messaging (FOLDER - feature flagged)

Refactored: 2026-01-12 - All folders consolidated into flat files
"""

from flask import Blueprint

# Create main API v1 blueprint
# This is THE ONLY api_v1 blueprint - parent package imports this!
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# =============================================================================
# FLAT FILE IMPORTS - All consolidated endpoints
# =============================================================================

# Core endpoints
from app.api.v1.auth import auth_bp
from app.api.v1.users import users_bp, users_part2_bp
from app.api.v1.profile import profile_bp
# Health is registered separately in app/__init__.py (not a blueprint)

# Content endpoints
from app.api.v1.courses import core_bp as courses_core_bp, crud_bp as courses_crud_bp, publishing_bp as courses_publishing_bp, enrollment_bp as courses_enrollment_bp
from app.api.v1.categories import admin_bp as categories_admin_bp, hierarchy_bp as categories_hierarchy_bp, public_bp as categories_public_bp
from app.api.v1.learning_methods import learning_methods_bp, chapter_theory_bp, lesson_explanations_bp, lesson_videos_bp
from app.api.v1.exam_simulations import exams_bp as exam_simulations_bp

# Billing endpoints
from app.api.v1.subscriptions import subscriptions_bp
from app.api.v1.tokens import tokens_bp

# Organisation endpoints
from app.api.v1.organisations import organisations_bp

# Feedback endpoints
from app.api.v1.feedback import feedback_bp

# AI/Tutor endpoints
from app.api.v1.tutor import tutor_bp, tutor_admin_bp
from app.api.v1.ai import agents_bp
from app.api.v1.tts import synthesis_bp as tts_bp, pronunciations_bp as tts_pronunciations_bp, audio_bp
from app.api.v1.math_toolkit import practice_bp as math_toolkit_practice_bp, reference_bp as math_toolkit_reference_bp, tasks_bp as math_toolkit_tasks_bp, admin_bp as math_toolkit_admin_bp

# Analytics endpoints
from app.api.v1.analytics import analytics_bp, org_analytics_bp

# Gamification endpoint
from app.api.v1.gamification import gamification_bp

# i18n endpoints (public + admin)
# Import both from barrel export for backward compatibility
from app.api.v1.i18n import public_bp as i18n_public_bp, admin_bp as i18n_admin_bp, translation_bp

# Feature-based authorization endpoints (public + authenticated)
from app.api.v1.features import features_bp

# Course Editor (feature-based - manual + AI editor)
from app.api.v1.course_editor import course_editor_bp

# =============================================================================
# FOLDER IMPORTS - Complex features that stay as folders
# =============================================================================

# Dashboard (complex - stays as folder)
from app.api.v1 import dashboard

# Admin Panel (complex - stays as folder)
# Note: importlib used because folder name contains hyphen
import importlib
admin_panel = importlib.import_module('app.api.v1.admin-panel')

# Feature-flagged packages
try:
    from app.api.v1 import social
except ImportError:
    social = None

try:
    from app.api.v1 import community
except ImportError:
    community = None

try:
    from app.api.v1 import messaging
except ImportError:
    messaging = None

# =============================================================================
# BLUEPRINT REGISTRATION
# =============================================================================

# Register all flat file blueprints
api_v1.register_blueprint(auth_bp)
api_v1.register_blueprint(users_bp)
api_v1.register_blueprint(users_part2_bp)
api_v1.register_blueprint(profile_bp)
# health_bp registered separately in app/__init__.py
api_v1.register_blueprint(courses_core_bp)
api_v1.register_blueprint(courses_crud_bp)
api_v1.register_blueprint(courses_publishing_bp)
api_v1.register_blueprint(courses_enrollment_bp)
api_v1.register_blueprint(categories_admin_bp)
api_v1.register_blueprint(categories_hierarchy_bp)
api_v1.register_blueprint(categories_public_bp)
api_v1.register_blueprint(learning_methods_bp)
api_v1.register_blueprint(chapter_theory_bp)
api_v1.register_blueprint(lesson_explanations_bp)
api_v1.register_blueprint(lesson_videos_bp)
api_v1.register_blueprint(exam_simulations_bp)
api_v1.register_blueprint(subscriptions_bp)
api_v1.register_blueprint(tokens_bp)
api_v1.register_blueprint(organisations_bp)
api_v1.register_blueprint(feedback_bp)
api_v1.register_blueprint(tutor_bp)
api_v1.register_blueprint(tutor_admin_bp)
api_v1.register_blueprint(agents_bp)
api_v1.register_blueprint(tts_bp)
api_v1.register_blueprint(tts_pronunciations_bp)
api_v1.register_blueprint(math_toolkit_practice_bp)
api_v1.register_blueprint(math_toolkit_reference_bp)
api_v1.register_blueprint(math_toolkit_tasks_bp)
api_v1.register_blueprint(math_toolkit_admin_bp)
api_v1.register_blueprint(analytics_bp)
api_v1.register_blueprint(org_analytics_bp)
api_v1.register_blueprint(gamification_bp)
api_v1.register_blueprint(audio_bp)
api_v1.register_blueprint(i18n_public_bp)
api_v1.register_blueprint(i18n_admin_bp)
api_v1.register_blueprint(translation_bp)
api_v1.register_blueprint(features_bp)
api_v1.register_blueprint(course_editor_bp)

# Dashboard and Admin blueprints registered in their own __init__.py files

# Export all
__all__ = [
    'api_v1',
    'auth_bp', 'users_bp', 'users_part2_bp', 'profile_bp', 'health_bp',
    'courses_core_bp', 'courses_crud_bp', 'courses_publishing_bp', 'courses_enrollment_bp', 'categories_admin_bp', 'categories_hierarchy_bp', 'categories_public_bp', 'learning_methods_bp',
    'chapter_theory_bp', 'lesson_explanations_bp', 'lesson_videos_bp', 'exam_simulations_bp',
    'subscriptions_bp', 'tokens_bp', 'organisations_bp', 'feedback_bp',
    'tutor_bp', 'tutor_admin_bp', 'agents_bp', 'tts_bp', 'tts_pronunciations_bp',
    'math_toolkit_practice_bp', 'math_toolkit_reference_bp', 'math_toolkit_tasks_bp', 'math_toolkit_admin_bp',
    'analytics_bp', 'org_analytics_bp', 'gamification_bp', 'audio_bp',
    'i18n_public_bp', 'i18n_admin_bp', 'translation_bp', 'features_bp', 'course_editor_bp',
    'dashboard', 'admin_panel', 'social', 'community', 'messaging'
]
