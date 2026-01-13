"""
Feedback System API

User feedback collection and management with DDD organization.

Structure:
- admin/     - Admin endpoints (list, status, priority, responses, summaries)
- user/      - User endpoints (submit, my feedback)
- core/      - Factory for feedback instance creation

Blueprints:
- feedback_user_bp   - User feedback submission (/api/v1/feedback/...)
- feedback_admin_bp  - Admin feedback management (/api/v1/feedback/...)

Example usage:
    >>> from app.api.shared.feedback.admin import bp as feedback_admin_bp
    >>> from app.api.shared.feedback.user import bp as feedback_user_bp
    >>> from app.api.shared.feedback.core import FeedbackFactory
"""

from flask import Blueprint
from app.api import api_v1

# Import sub-blueprints
from app.api.shared.feedback.admin import bp as admin_bp
from app.api.shared.feedback.user import bp as user_bp

# Create main blueprint
feedback_bp = Blueprint('feedback', __name__, url_prefix='/feedback')

# Register sub-blueprints
# Admin routes: /api/v1/feedback/... (with admin auth)
feedback_bp.register_blueprint(admin_bp, url_prefix='')

# User routes: /api/v1/feedback/submit, /api/v1/feedback/my
feedback_bp.register_blueprint(user_bp, url_prefix='')

# Register with API v1
api_v1.register_blueprint(feedback_bp)

__all__ = ['feedback_bp', 'admin_bp', 'user_bp']
