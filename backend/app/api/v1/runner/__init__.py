"""
LernsystemX Runner API v1

Execution endpoints for learning sessions.
Runner API - Execution ONLY, NO configuration logic.

Blueprints:
- sessions: Session lifecycle (start, state, finish)
"""

from flask import Blueprint

# Create parent blueprint for runner routes
runner_bp = Blueprint('runner', __name__, url_prefix='/runner')

# Import child blueprints
from app.api.v1.runner.sessions import bp as sessions_bp

__all__ = [
    'runner_bp',
    'sessions_bp'
]
