"""
MathToolkit API Package - Endpoints für das Mathe-Lern-System

Refactored into 4 focused packages:
    - calculator/ - Taschenrechner-Funktionen
    - reference/  - Kategorien, Patterns, Formeln
    - sessions/   - Übungssitzungen
    - interactive/- User-Fortschritt, Hints, Tasks, Admin

Structure:
    calculator/
        ├── __init__.py
        └── engine.py         ~85 LOC  - /calculator/evaluate, /calculator/history, /calculator/save

    reference/
        ├── __init__.py
        └── library.py       ~135 LOC  - /categories, /patterns, /formulas

    sessions/
        ├── __init__.py
        └── history.py       ~125 LOC  - /sessions CRUD, /sessions/:id/steps

    interactive/
        ├── __init__.py
        └── exercises.py     ~215 LOC  - /progress, /hints, /tasks, /admin/*

Route Registration:
    Blueprint created here, imported by sub-modules, registered on api_v1.
    Final URLs: /api/v1/math-toolkit/*

Refactored: 2026-01-08 per Developer-Guide-KI Section 10
"""

from flask import Blueprint
from app.api import api_v1

# Create blueprint FIRST (before importing sub-modules)
math_toolkit_bp = Blueprint('math_toolkit', __name__, url_prefix='/math-toolkit')

# NOW import all route modules to register endpoints
# (they will import math_toolkit_bp from this module)
from app.api.system_features.math.calculator import engine
from app.api.system_features.math.reference import library
from app.api.system_features.math.sessions import history
from app.api.system_features.math.interactive import exercises

# Register blueprint with main API
api_v1.register_blueprint(math_toolkit_bp)

__all__ = ['math_toolkit_bp']
