"""
Feedback User Submission - User endpoints for feedback system.

Endpoints:
- POST /feedback/submit - Submit feedback (works without auth for anonymous)
- GET /feedback/my - Get user's own feedback
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request

from app.services.feedback_service import FeedbackService
from app.repositories.feedback.core import FeedbackRepository

bp = Blueprint('feedback_user', __name__)


# =============================================================================
# PUBLIC SUBMISSION (with optional auth)
# =============================================================================

@bp.route('/submit', methods=['POST'])
def submit_feedback():
    """
    Submit user feedback.

    Can be used with or without authentication.
    Anonymous feedback is allowed.
    """
    data = request.get_json()

    if not data:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_REQUEST', 'message': 'No data provided'}
        }), 400

    # Get user_id if authenticated (optional)
    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except Exception:
        pass

    # Extract data
    feedback_type = data.get('type')
    message = data.get('message')
    title = data.get('title')
    email = data.get('email')
    is_anonymous = data.get('is_anonymous', False)
    context = data.get('context', {})

    # Validation
    if not feedback_type:
        return jsonify({
            'success': False,
            'error': {'code': 'MISSING_TYPE', 'message': 'Feedback type is required'}
        }), 400

    if not message:
        return jsonify({
            'success': False,
            'error': {'code': 'MISSING_MESSAGE', 'message': 'Message is required'}
        }), 400

    # Submit
    feedback, error = FeedbackService.submit_feedback(
        feedback_type=feedback_type,
        message=message,
        title=title,
        user_id=user_id,
        email=email,
        is_anonymous=is_anonymous,
        context=context
    )

    if error:
        return jsonify({
            'success': False,
            'error': {'code': 'SUBMIT_FAILED', 'message': error}
        }), 400

    return jsonify({
        'success': True,
        'data': {
            'feedback_id': str(feedback['feedback_id']),
            'message': 'Feedback erfolgreich gesendet'
        }
    }), 201


# =============================================================================
# AUTHENTICATED USER ENDPOINTS
# =============================================================================

@bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_feedback():
    """Get current user's submitted feedback."""
    user_id = get_jwt_identity()

    feedbacks = FeedbackRepository.get_recent_by_user(user_id, limit=20)

    return jsonify({
        'success': True,
        'data': {
            'feedbacks': feedbacks
        }
    })
