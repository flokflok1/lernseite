"""
Exam Simulations API Package

IHK-style exam simulations with intelligent question generation.

Structure:
- user/ - User-facing exam simulation endpoints (CRUD, attempts, settings)

Consolidated from: exam_simulations/ root files → exam_simulations/user/ (Batch 5, Phase 7)

Endpoints (9 total):
- POST /courses/:course_id/exam-simulations - Create simulation
- GET /exam-simulations - List user's simulations
- GET /exam-simulations/:id - Get simulation details
- DELETE /exam-simulations/:id - Delete simulation
- POST /exam-simulations/:id/start - Start attempt
- GET /exam-simulations/:id/attempts - List attempts
- POST /exam-simulations/:id/submit - Submit answers
- GET /user-profile/exam-settings - Get exam profile
- PUT /user-profile/exam-settings - Update exam profile

ISO 9001:2015 compliant - Assessment & Evaluation Layer
"""

from flask import Blueprint

# Import blueprints from user module
from app.api.v1.system_features.exam_simulations.user.core import core_bp, course_bp
from app.api.v1.system_features.exam_simulations.user.attempts import attempts_bp
from app.api.v1.system_features.exam_simulations.user.settings import settings_bp

# Create main blueprint (barrel export)
exams_bp = Blueprint('exam_simulations', __name__, url_prefix='')

# Register all child blueprints
exams_bp.register_blueprint(core_bp)
exams_bp.register_blueprint(course_bp)
exams_bp.register_blueprint(attempts_bp)
exams_bp.register_blueprint(settings_bp)

__all__ = ['exams_bp']
