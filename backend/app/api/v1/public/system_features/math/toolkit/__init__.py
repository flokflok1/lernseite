"""
Math Toolkit API Package

Mathematical toolkit with practice sessions, reference library, and admin management.

Structure:
- admin/ - Admin pattern/formula management
- user/ - User practice sessions, reference library, tasks

Consolidated from: math_toolkit/ root files (Batch 5, Phase 7)

Endpoints (User):
- POST /math-toolkit/calculator/evaluate - Evaluate expression
- GET /math-toolkit/calculator/history - Calculator history
- POST /math-toolkit/sessions - Start practice session
- GET /math-toolkit/reference - Browse reference library
- POST /math-toolkit/tasks - Task validation

Endpoints (Admin):
- POST /math-toolkit/admin/patterns - Create calculation pattern
- POST /math-toolkit/admin/formulas - Create formula

ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from app.api.v1.system_features.math.toolkit.admin.routes import admin_bp
from app.api.v1.system_features.math.toolkit.user.practice import practice_bp
from app.api.v1.system_features.math.toolkit.user.reference import reference_bp
from app.api.v1.system_features.math.toolkit.user.tasks import tasks_bp

__all__ = ['admin_bp', 'practice_bp', 'reference_bp', 'tasks_bp']
