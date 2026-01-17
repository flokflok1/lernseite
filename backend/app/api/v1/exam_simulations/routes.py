"""
LernsystemX Exam Simulations API - Barrel Export

Consolidated exam simulation management for IHK-style exams.

Endpoints (9 total across 3 modules):
- Core (4): POST /courses/:course_id/exam-simulations, GET /exam-simulations, GET /exam-simulations/:id, DELETE /exam-simulations/:id
- Attempts (3): POST /exam-simulations/:id/start, GET /exam-simulations/:id/attempts, POST /exam-simulations/:id/submit
- Settings (2): GET /user-profile/exam-settings, PUT /user-profile/exam-settings

Architecture: Semantic splitting with dedicated modules
- exam_simulations_core.py - Simulation CRUD + ExamService
- exam_simulations_attempts.py - Attempt management
- exam_simulations_settings.py - User profile/settings

ISO 9001:2015 compliant - Assessment & Evaluation Layer
Refactored: 2026-01-16 - Semantic function grouping (Phase 2)
"""

from flask import Blueprint

# Import all submodule blueprints
from app.api.v1.exam_simulations.core import core_bp as exam_simulations_core_bp, course_bp as exam_simulations_course_bp
from app.api.v1.exam_simulations.attempts import attempts_bp as exam_simulations_attempts_bp
from app.api.v1.exam_simulations.settings import settings_bp as exam_user_profile_bp

# Create main blueprint (barrel export)
exams_bp = Blueprint('exam_simulations', __name__, url_prefix='')

# Register all submodule blueprints as child blueprints
# This ensures all routes from submodules are available under /api/v1/*
exams_bp.register_blueprint(exam_simulations_core_bp)
exams_bp.register_blueprint(exam_simulations_course_bp)
exams_bp.register_blueprint(exam_simulations_attempts_bp)
exams_bp.register_blueprint(exam_user_profile_bp)

# All route handlers are now in submodules:
# - exam_simulations_core_bp: Simulation management (CRUD)
# - exam_simulations_course_bp: Course-specific simulation creation
# - exam_simulations_attempts_bp: Exam attempt management
# - exam_user_profile_bp: User exam profile/settings

__all__ = ['exams_bp']
