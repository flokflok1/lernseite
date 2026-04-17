"""
LernsystemX API v1 Package

Consolidated API structure:
├── v1/
│   ├── panel/
│   │   ├── admin/         # Admin-only endpoints (analytics, users, settings, ...)
│   │   ├── editor/        # Course editor (manual + AI)
│   │   └── user/          # User-facing panel (profile, dashboard, gamification, ...)
│   ├── public/            # Unauthenticated endpoints (auth, business, categories, ...)
│   ├── public/system_features/  # 25 System-Features (10 categories)
│   ├── community/         # Feature-flagged
│   ├── messaging/         # Feature-flagged
│   └── social/            # Feature-flagged

Refactored: 2026-02-15 - Consolidated 30+ top-level dirs into panel/admin, panel/editor,
panel/user, public + system_features. Blueprint url_prefix values are UNCHANGED.
"""

from flask import Blueprint
import sys
import importlib

# Create main API v1 blueprint
# This is THE ONLY api_v1 blueprint - parent package imports this!
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# =============================================================================
# PUBLIC ENDPOINTS — Unauthenticated
# =============================================================================

from app.api.v1.public.auth import auth_bp
# TODO: B2B signup temporarily disabled until AuthService is created
# from app.api.v1.public.auth.b2b_signup import bp as b2b_signup_bp
from app.api.v1.public.business import bp as business_contact_bp
from app.api.v1.public.courses.core import core_bp as courses_core_bp
from app.api.v1.public.courses.crud import crud_bp as courses_crud_bp
from app.api.v1.public.courses.publishing import publishing_bp as courses_publishing_bp
from app.api.v1.public.courses.enrollment import enrollment_bp as courses_enrollment_bp
from app.api.v1.public.courses.lessons import lessons_bp as lessons_public_bp
from app.api.v1.public.categories import public_bp as categories_public_bp, hierarchy_bp as categories_hierarchy_bp
from app.api.v1.public.learning_methods import learning_methods_bp, learning_methods_catalog_bp, chapter_theory_bp, lesson_explanations_bp, lesson_videos_bp
from app.api.v1.public.features import features_bp, features_catalog_bp

# =============================================================================
# PANEL ADMIN ENDPOINTS — Admin-only
# =============================================================================

from app.api.v1.panel.admin.users import users_bp, users_part2_bp
from app.api.v1.panel.admin.categories import admin_bp as categories_admin_bp
from app.api.v1.panel.admin.subscriptions import subscriptions_bp
from app.api.v1.panel.admin.billing.admin import admin_tokens_bp
from app.api.v1.panel.admin.organisations import organisations_bp
from app.api.v1.panel.admin.feedback import feedback_bp
from app.api.v1.panel.admin.tutor.admin import tutor_admin_bp
from app.api.v1.panel.admin import ai as ai_admin  # Triggers AI admin blueprint registration
from app.api.v1.panel.admin.analytics import analytics_bp, org_analytics_bp
from app.api.v1.panel.admin import courses as courses_admin  # Triggers admin route registration
from app.api.v1.panel.admin import exams as exams_admin  # Triggers exam archive blueprint registration
from app.api.v1.panel.admin import crawler as crawler_admin  # noqa: F401 — triggers crawler blueprint registration
from app.api.v1.panel.admin.programs import programs_admin_bp, program_types_bp, exam_types_bp
from app.api.v1.panel.admin.topics import topics_admin_bp

# Prompts Library (CRUD, actions, categories)
from app.api.v1.panel.admin.prompts import crud as _prompts_crud, actions as _prompts_actions, categories as _prompts_categories  # noqa: F401 — triggers route registration
from app.api.v1.panel.admin.prompts.blueprints import prompts_crud_bp, prompts_actions_bp, prompts_categories_bp

# Dashboard admin blueprints (importlib for dynamic import)
try:
    dashboard_admin_stats = importlib.import_module('.stats', package='app.api.v1.panel.admin.dashboard')
    dashboard_admin_stats_bp = dashboard_admin_stats.bp

    dashboard_admin_system = importlib.import_module('.system', package='app.api.v1.panel.admin.dashboard')
    dashboard_admin_system_bp = dashboard_admin_system.bp
except (ImportError, AttributeError) as e:
    print(f"ERROR: Failed to extract dashboard admin blueprints: {e}")
    raise

# Learning Methods Admin - Schema endpoint for dynamic form rendering
from app.api.v1.panel.admin.learning_methods import routes as learning_methods_admin
learning_methods_admin_bp = learning_methods_admin.bp

# Groups Admin - GBA (Group-Based Authorization) management
from app.api.v1.panel.admin.groups import routes as admin_groups
admin_groups_bp = admin_groups.bp

# Feature Flags - Feature flag configuration and rollout management
from app.api.v1.panel.admin.features.flags import feature_flags_bp, rollout_plans_crud_bp, rollout_plans_actions_bp

# Feature Configuration - Enterprise feature management
from app.api.v1.panel.admin.features.configuration import (
    feature_config_core_bp,
    feature_config_core_part2_bp,
    feature_config_rollout_bp,
    feature_config_ab_tests_bp,
    feature_config_audit_bp
)

# =============================================================================
# PANEL EDITOR ENDPOINTS — Course editor
# =============================================================================

from app.api.v1.panel.editor import course_editor_bp

# =============================================================================
# PANEL USER ENDPOINTS — User-facing panel
# =============================================================================

from app.api.v1.panel.user.profile import profile_bp
from app.api.v1.panel.user.billing.user import tokens_bp
from app.api.v1.panel.user.tutor.user import tutor_bp
from app.api.v1.panel.user.agents.agents import agents_bp
from app.api.v1.panel.user.tts import synthesis_bp as tts_bp, pronunciations_bp as tts_pronunciations_bp, audio_bp
from app.api.v1.panel.user.gamification import gamification_bp
from app.api.v1.panel.user import dashboard
from app.api.v1.panel.user.dashboard import widgets_registry_bp, widgets_instances_bp
from app.api.v1.panel.user.runner import sessions_bp as runner_sessions_bp
from app.api.v1.panel.user.exams import trainer_bp as exam_trainer_bp
from app.api.v1.panel.user.exams import exam_upload_bp
from app.api.v1.panel.user.exams import ap2_trainer_bp
from app.api.v1.panel.user.exam_goals import exam_goals_bp
from app.api.v1.panel.user.learning.reviews import review_bp
from app.api.v1.panel.user.programs import programs_user_bp

# =============================================================================
# i18n ENDPOINTS — Reconstructed from 4 packages (was I18N_BLUEPRINTS list)
# =============================================================================

# Public i18n
from app.api.v1.public.i18n import i18n_keys_bp, i18n_languages_bp, i18n_public_bp
# Admin i18n
from app.api.v1.panel.admin.i18n import i18n_admin_bp, i18n_sync_bp, admin_translations_bp
from app.api.v1.panel.admin.i18n.moderation import i18n_moderation_bp, i18n_suggestions_bp
from app.api.v1.panel.admin.i18n.translations.ai_translation import i18n_ai_translation_bp
from app.api.v1.panel.admin.i18n.translations.translation_api import bp as translation_bp

I18N_BLUEPRINTS = [
    i18n_keys_bp, i18n_languages_bp, i18n_public_bp,
    i18n_admin_bp, i18n_sync_bp, admin_translations_bp,
    i18n_moderation_bp, i18n_suggestions_bp,
    i18n_ai_translation_bp, translation_bp,
]

# =============================================================================
# SYSTEM FEATURES — 25 System-Features (Interactive, Exam, Math, etc.) — UNCHANGED
# =============================================================================

from app.api.v1.public.system_features.exam import exams_bp as exam_simulations_bp
from app.api.v1.public.system_features.math import math_practice_bp as math_toolkit_practice_bp, math_reference_bp as math_toolkit_reference_bp, math_tasks_bp as math_toolkit_tasks_bp
from app.api.v1.panel.admin.math_toolkit import admin_bp as math_toolkit_admin_bp
from app.api.v1.public.system_features import system_features_bp, registry_bp as panel_system_features_bp

# =============================================================================
# PANEL CONFIG — Runner modes, LM type compatibility
# =============================================================================

from app.api.v1.panel import (
    runner_modes_bp as panel_runner_modes_bp,
    lm_type_compatibility_bp as panel_lm_type_compatibility_bp
)

# =============================================================================
# FEATURE-FLAGGED PACKAGES — UNCHANGED
# =============================================================================

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

# Public endpoints
api_v1.register_blueprint(auth_bp)
# TODO: B2B signup temporarily disabled until AuthService is created
# api_v1.register_blueprint(b2b_signup_bp)
api_v1.register_blueprint(business_contact_bp)
api_v1.register_blueprint(courses_core_bp)
api_v1.register_blueprint(courses_crud_bp)
api_v1.register_blueprint(courses_publishing_bp)
api_v1.register_blueprint(courses_enrollment_bp)
api_v1.register_blueprint(lessons_public_bp)
api_v1.register_blueprint(categories_public_bp)
api_v1.register_blueprint(categories_hierarchy_bp)
api_v1.register_blueprint(learning_methods_bp)
api_v1.register_blueprint(learning_methods_catalog_bp)
api_v1.register_blueprint(chapter_theory_bp)
api_v1.register_blueprint(lesson_explanations_bp)
api_v1.register_blueprint(lesson_videos_bp)
api_v1.register_blueprint(features_bp)
api_v1.register_blueprint(features_catalog_bp)

# Panel admin endpoints
api_v1.register_blueprint(users_bp)
api_v1.register_blueprint(users_part2_bp)
api_v1.register_blueprint(categories_admin_bp)
api_v1.register_blueprint(subscriptions_bp)
api_v1.register_blueprint(admin_tokens_bp)
api_v1.register_blueprint(organisations_bp)
api_v1.register_blueprint(feedback_bp)
api_v1.register_blueprint(tutor_admin_bp)
api_v1.register_blueprint(analytics_bp)
api_v1.register_blueprint(org_analytics_bp)
api_v1.register_blueprint(dashboard_admin_stats_bp)
api_v1.register_blueprint(dashboard_admin_system_bp)
api_v1.register_blueprint(learning_methods_admin_bp)
api_v1.register_blueprint(admin_groups_bp)
api_v1.register_blueprint(feature_flags_bp)
api_v1.register_blueprint(rollout_plans_crud_bp)
api_v1.register_blueprint(rollout_plans_actions_bp)
api_v1.register_blueprint(feature_config_core_bp)
api_v1.register_blueprint(feature_config_core_part2_bp)
api_v1.register_blueprint(feature_config_rollout_bp)
api_v1.register_blueprint(feature_config_ab_tests_bp)
api_v1.register_blueprint(feature_config_audit_bp)

# Programs admin
api_v1.register_blueprint(programs_admin_bp)
api_v1.register_blueprint(program_types_bp)
api_v1.register_blueprint(exam_types_bp)

# Topics admin (topic hierarchy management)
api_v1.register_blueprint(topics_admin_bp)

# Prompts Library
api_v1.register_blueprint(prompts_crud_bp)
api_v1.register_blueprint(prompts_actions_bp)
api_v1.register_blueprint(prompts_categories_bp)

# Panel editor endpoints
api_v1.register_blueprint(course_editor_bp)

# Panel user endpoints
api_v1.register_blueprint(profile_bp)
api_v1.register_blueprint(tokens_bp)
api_v1.register_blueprint(tutor_bp)
api_v1.register_blueprint(agents_bp)
api_v1.register_blueprint(tts_bp)
api_v1.register_blueprint(tts_pronunciations_bp)
api_v1.register_blueprint(audio_bp)
api_v1.register_blueprint(gamification_bp)
api_v1.register_blueprint(widgets_registry_bp)
api_v1.register_blueprint(widgets_instances_bp)
api_v1.register_blueprint(runner_sessions_bp)
api_v1.register_blueprint(exam_trainer_bp)
api_v1.register_blueprint(exam_upload_bp)
api_v1.register_blueprint(ap2_trainer_bp)
api_v1.register_blueprint(exam_goals_bp)
api_v1.register_blueprint(review_bp)
api_v1.register_blueprint(programs_user_bp)

# i18n blueprints (reconstructed from 4 packages)
for _i18n_bp in I18N_BLUEPRINTS:
    api_v1.register_blueprint(_i18n_bp)

# System Features (25 Features in 10 Categories)
api_v1.register_blueprint(system_features_bp)
api_v1.register_blueprint(exam_simulations_bp)
api_v1.register_blueprint(math_toolkit_practice_bp)
api_v1.register_blueprint(math_toolkit_reference_bp)
api_v1.register_blueprint(math_toolkit_tasks_bp)
api_v1.register_blueprint(math_toolkit_admin_bp)

# Panel config
api_v1.register_blueprint(panel_runner_modes_bp)
api_v1.register_blueprint(panel_lm_type_compatibility_bp)
api_v1.register_blueprint(panel_system_features_bp)

# Community (feature-flagged)
if groups_bp:
    api_v1.register_blueprint(groups_bp)

# Export all
__all__ = [
    'api_v1',
    # Public
    'auth_bp', 'business_contact_bp',
    'courses_core_bp', 'courses_crud_bp', 'courses_publishing_bp', 'courses_enrollment_bp', 'lessons_public_bp',
    'categories_public_bp', 'categories_hierarchy_bp',
    'learning_methods_bp', 'learning_methods_catalog_bp', 'chapter_theory_bp',
    'lesson_explanations_bp', 'lesson_videos_bp',
    'features_bp', 'features_catalog_bp',
    # Panel admin
    'users_bp', 'users_part2_bp', 'categories_admin_bp',
    'subscriptions_bp', 'admin_tokens_bp', 'organisations_bp', 'feedback_bp',
    'tutor_admin_bp', 'analytics_bp', 'org_analytics_bp',
    'dashboard_admin_stats_bp', 'dashboard_admin_system_bp',
    'learning_methods_admin_bp', 'admin_groups_bp',
    'feature_flags_bp', 'rollout_plans_crud_bp', 'rollout_plans_actions_bp',
    'feature_config_core_bp', 'feature_config_core_part2_bp',
    'feature_config_rollout_bp', 'feature_config_ab_tests_bp', 'feature_config_audit_bp',
    'programs_admin_bp', 'program_types_bp', 'exam_types_bp', 'topics_admin_bp',
    'prompts_crud_bp', 'prompts_actions_bp', 'prompts_categories_bp',
    # Panel editor
    'course_editor_bp',
    # Panel user
    'profile_bp', 'tokens_bp', 'tutor_bp', 'agents_bp',
    'tts_bp', 'tts_pronunciations_bp', 'audio_bp',
    'gamification_bp', 'widgets_registry_bp', 'widgets_instances_bp',
    'runner_sessions_bp', 'exam_trainer_bp', 'ap2_trainer_bp', 'exam_goals_bp', 'review_bp',
    'programs_user_bp',
    # i18n
    'I18N_BLUEPRINTS',
    # System features
    'system_features_bp', 'panel_system_features_bp',
    'exam_simulations_bp',
    'math_toolkit_practice_bp', 'math_toolkit_reference_bp',
    'math_toolkit_tasks_bp', 'math_toolkit_admin_bp',
    # Panel config
    'panel_runner_modes_bp', 'panel_lm_type_compatibility_bp',
    # Feature-flagged
    'groups_bp', 'dashboard', 'social', 'community', 'messaging',
]
