"""
Daily Recall - System Feature (Gamification)

Returns the user's top due review items across all courses.
Uses the SM-2 spaced repetition system for scheduling.
"""
import logging
from flask import Blueprint, request
from app.api.middleware.auth import token_required, get_current_user
from app.api.responses.responses import success_response

logger = logging.getLogger(__name__)

daily_recall_bp = Blueprint('daily_recall', __name__, url_prefix='/gamification/daily-recall')


@daily_recall_bp.route('/questions', methods=['GET'])
@token_required
def get_daily_questions():
    """Get today's due review items for the current user."""
    user = get_current_user()
    try:
        limit = min(int(request.args.get('limit', 10)), 50)
    except (ValueError, TypeError):
        limit = 10

    from app.application.services.learning.review_service import ReviewService
    result = ReviewService.get_daily_recall(user['user_id'], limit)
    return success_response(data=result)
