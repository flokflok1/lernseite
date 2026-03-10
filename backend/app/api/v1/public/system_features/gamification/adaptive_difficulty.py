"""
Adaptive Difficulty - System Feature (Gamification)

Provides difficulty recommendations based on user's mastery level.
Uses SM-2 spaced repetition data to determine optimal difficulty.
"""
import logging
from flask import Blueprint, request
from app.api.middleware.auth import token_required, get_current_user
from app.api.responses.responses import success_response, error_response
from app.infrastructure.i18n.error_codes import ErrorCode

logger = logging.getLogger(__name__)

adaptive_difficulty_bp = Blueprint(
    'adaptive_difficulty', __name__,
    url_prefix='/gamification/adaptive-difficulty',
)


@adaptive_difficulty_bp.route('/adjust', methods=['POST'])
@token_required
def adjust_difficulty():
    """Receive a method_id and return its current difficulty state."""
    user = get_current_user()
    data = request.json or {}
    method_id = data.get('method_id')
    if not method_id:
        return error_response(ErrorCode.VALIDATION_ERROR, details={'field': 'method_id', 'message': 'required'})

    from app.application.services.learning.review_service import ReviewService
    result = ReviewService.get_method_difficulty(user['user_id'], method_id)
    return success_response(data=result)


@adaptive_difficulty_bp.route('/recommendation', methods=['GET'])
@token_required
def get_recommendation():
    """Get difficulty recommendation for a course."""
    user = get_current_user()
    course_id = request.args.get('course_id')
    if not course_id:
        return error_response(ErrorCode.VALIDATION_ERROR, details={'field': 'course_id', 'message': 'required'})

    from app.application.services.learning.review_service import ReviewService
    result = ReviewService.get_course_difficulty(user['user_id'], course_id)
    return success_response(data=result)
