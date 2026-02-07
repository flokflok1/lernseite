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
import sys

# Create main API v1 blueprint
# This is THE ONLY api_v1 blueprint - parent package imports this!
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# =============================================================================
# FLAT FILE IMPORTS - All consolidated endpoints
# =============================================================================

# Core endpoints
from app.api.v1.auth import auth_bp
# TODO: B2B signup temporarily disabled until AuthService is created
# from app.api.v1.auth.b2b_signup import bp as b2b_signup_bp  # ← NEW: B2B signup endpoint
from app.api.v1.business import bp as business_contact_bp  # ← NEW: B2B contact form endpoint
from app.api.v1.users import users_bp, users_part2_bp
from app.api.v1.profile import profile_bp
# Health is registered separately in app/__init__.py (not a blueprint)

# Content endpoints
from app.api.v1.courses import core_bp as courses_core_bp, crud_bp as courses_crud_bp, publishing_bp as courses_publishing_bp, enrollment_bp as courses_enrollment_bp
from app.api.v1.categories import admin_bp as categories_admin_bp, hierarchy_bp as categories_hierarchy_bp, public_bp as categories_public_bp
from app.api.v1.learning_methods import learning_methods_bp, learning_methods_catalog_bp, chapter_theory_bp, lesson_explanations_bp, lesson_videos_bp
from app.api.v1.exam_simulations import exams_bp as exam_simulations_bp

# Billing endpoints
from app.api.v1.subscriptions import subscriptions_bp
from app.api.v1.billing.tokens import tokens_bp, admin_tokens_bp

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

# i18n endpoints are registered via app.i18n package
# DO NOT import from app.api.v1.i18n - that creates duplicate blueprint names
# The app.i18n package handles all i18n blueprint registration

# Feature-based authorization endpoints (public + authenticated)
from app.api.v1.features import features_bp, features_catalog_bp

# Course Editor (feature-based - manual + AI editor)
from app.api.v1.course_editor import course_editor_bp

# =============================================================================
# FOLDER IMPORTS - Complex features that stay as folders
# =============================================================================

# Dashboard (complex - stays as folder)
from app.api.v1 import dashboard

# Admin Panel (complex - stays as folder)
import importlib
admin_panel = importlib.import_module('.admin', package='app.api.v1')

# Admin Dashboard - Extract blueprint from dashboard module
# Dashboard statistics endpoints (fixed SQL queries with schema-prefixed table names)
try:
    admin_dashboard = importlib.import_module('.dashboard', package='app.api.v1.admin')
    admin_dashboard_bp = admin_dashboard.bp
except (ImportError, AttributeError) as e:
    print(f"ERROR: Failed to extract admin_dashboard blueprint: {e}")
    raise

# Admin Learning Methods - Extract blueprint from learning_methods module
# Learning methods schema endpoint for dynamic form rendering
try:
    learning_methods_admin = importlib.import_module('.learning_methods', package='app.api.v1.admin')
    learning_methods_admin_bp = learning_methods_admin.bp
except (ImportError, AttributeError) as e:
    print(f"ERROR: Failed to extract learning_methods blueprint: {e}")
    raise

# Admin Groups - Extract blueprint from groups module
# GBA (Group-Based Authorization) management endpoints
try:
    admin_groups = importlib.import_module('.groups', package='app.api.v1.admin')
    admin_groups_bp = admin_groups.bp
except (ImportError, AttributeError) as e:
    print(f"ERROR: Failed to extract admin_groups blueprint: {e}")
    raise

# Admin Translations - Deterministic helpers for translation management
try:
    admin_translations = importlib.import_module('.translations', package='app.api.v1.admin')
    admin_translations_bp = admin_translations.bp
except (ImportError, AttributeError) as e:
    print(f"ERROR: Failed to extract admin_translations blueprint: {e}")
    raise

# Admin Settings - Extract feature_flags blueprints from settings module
# First, ensure settings module is loaded by accessing it from admin_panel
try:
    settings = importlib.import_module('.settings', package='app.api.v1.admin')
    feature_flags = importlib.import_module('.feature_flags', package='app.api.v1.admin.settings')
    feature_flags_bp = feature_flags.feature_flags_bp
    rollout_plans_crud_bp = feature_flags.rollout_plans_crud_bp
    rollout_plans_actions_bp = feature_flags.rollout_plans_actions_bp
except (ImportError, AttributeError) as e:
    print(f"ERROR: Failed to extract feature_flags blueprints: {e}")
    raise

# Feature Configuration Admin API (Phase 3 - Enterprise Feature Management)
feature_configuration = importlib.import_module('.feature-configuration', package='app.api.v1.admin')
feature_config_core_bp = feature_configuration.core_bp
feature_config_core_part2_bp = feature_configuration.core_part2_bp
feature_config_rollout_bp = feature_configuration.rollout_bp
feature_config_ab_tests_bp = feature_configuration.ab_tests_bp
feature_config_audit_bp = feature_configuration.audit_bp

# =============================================================================
# PANEL API - Configuration / Administration
# =============================================================================
from app.api.v1.panel import (
    runner_modes_bp as panel_runner_modes_bp,
    lm_type_compatibility_bp as panel_lm_type_compatibility_bp,
    system_features_bp as panel_system_features_bp
)

# =============================================================================
# RUNNER API - Execution / Learning / Exams
# =============================================================================
from app.api.v1.runner import sessions_bp as runner_sessions_bp


# Feature-flagged packages
try:
    from app.api.v1 import social
except ImportError:
    social = None

try:
    from app.api.v1.community import groups_bp
except ImportError:
    groups_bp = None

try:
    from app.api.v1 import messaging
except ImportError:
    messaging = None

# =============================================================================
# BLUEPRINT REGISTRATION
# =============================================================================

# Register all flat file blueprints
api_v1.register_blueprint(auth_bp)
# TODO: B2B signup temporarily disabled until AuthService is created
# api_v1.register_blueprint(b2b_signup_bp)  # ← NEW: Register B2B signup endpoint
api_v1.register_blueprint(business_contact_bp)  # ← NEW: Register B2B contact form endpoint
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
api_v1.register_blueprint(learning_methods_catalog_bp)
api_v1.register_blueprint(chapter_theory_bp)
api_v1.register_blueprint(lesson_explanations_bp)
api_v1.register_blueprint(lesson_videos_bp)
api_v1.register_blueprint(exam_simulations_bp)
api_v1.register_blueprint(subscriptions_bp)
api_v1.register_blueprint(tokens_bp)
api_v1.register_blueprint(admin_tokens_bp)
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
# i18n blueprints registered via app.i18n package (avoid duplicate names)
api_v1.register_blueprint(features_bp)
api_v1.register_blueprint(features_catalog_bp)
api_v1.register_blueprint(course_editor_bp)

# Register admin-panel dashboard blueprint
api_v1.register_blueprint(admin_dashboard_bp)

# Register admin-panel learning-methods blueprint
api_v1.register_blueprint(learning_methods_admin_bp)

# Register admin-panel groups blueprint (GBA - Group-Based Authorization)
api_v1.register_blueprint(admin_groups_bp)

# Register admin-panel translations blueprint (language draft helper)
api_v1.register_blueprint(admin_translations_bp)

# Register admin-panel settings blueprints (feature_flags)
api_v1.register_blueprint(feature_flags_bp)
api_v1.register_blueprint(rollout_plans_crud_bp)
api_v1.register_blueprint(rollout_plans_actions_bp)

# Register admin-panel feature-configuration blueprints (Phase 3 - Enterprise Feature Management)
api_v1.register_blueprint(feature_config_core_bp)
api_v1.register_blueprint(feature_config_core_part2_bp)
api_v1.register_blueprint(feature_config_rollout_bp)
api_v1.register_blueprint(feature_config_ab_tests_bp)
api_v1.register_blueprint(feature_config_audit_bp)

# Register community blueprints (GBA - Group-Based Access Control)
if groups_bp:
    api_v1.register_blueprint(groups_bp)

# =============================================================================
# PANEL API - Configuration / Administration
# =============================================================================
api_v1.register_blueprint(panel_runner_modes_bp)
api_v1.register_blueprint(panel_lm_type_compatibility_bp)
api_v1.register_blueprint(panel_system_features_bp)

# =============================================================================
# RUNNER API - Execution / Learning / Exams
# =============================================================================
api_v1.register_blueprint(runner_sessions_bp)

# Export all
__all__ = [
    'api_v1',
    'auth_bp', 'business_contact_bp', 'users_bp', 'users_part2_bp', 'profile_bp', 'health_bp',
    'courses_core_bp', 'courses_crud_bp', 'courses_publishing_bp', 'courses_enrollment_bp', 'categories_admin_bp', 'categories_hierarchy_bp', 'categories_public_bp', 'learning_methods_bp',
    'chapter_theory_bp', 'lesson_explanations_bp', 'lesson_videos_bp', 'exam_simulations_bp',
    'subscriptions_bp', 'tokens_bp', 'admin_tokens_bp', 'organisations_bp', 'feedback_bp',
    'tutor_bp', 'tutor_admin_bp', 'agents_bp', 'tts_bp', 'tts_pronunciations_bp',
    'math_toolkit_practice_bp', 'math_toolkit_reference_bp', 'math_toolkit_tasks_bp', 'math_toolkit_admin_bp',
    'analytics_bp', 'org_analytics_bp', 'gamification_bp', 'audio_bp',
    'features_bp', 'course_editor_bp',
    'learning_methods_admin_bp',
    'admin_groups_bp',
    'admin_translations_bp',
    'feature_flags_bp', 'rollout_plans_crud_bp', 'rollout_plans_actions_bp',
    'feature_config_core_bp', 'feature_config_core_part2_bp', 'feature_config_rollout_bp', 'feature_config_ab_tests_bp', 'feature_config_audit_bp',
    'groups_bp',
    # Panel API - Configuration / Administration
    'panel_runner_modes_bp', 'panel_lm_type_compatibility_bp', 'panel_system_features_bp',
    # Runner API - Execution / Learning / Exams
    'runner_sessions_bp',
    'dashboard', 'admin_panel', 'social', 'community', 'messaging'
]
