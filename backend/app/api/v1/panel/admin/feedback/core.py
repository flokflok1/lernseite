"""
LernsystemX Feedback API - Consolidated

Endpoints:
- POST /feedback/submit - Submit feedback (works without auth for anonymous)
- GET /feedback/my - Get user's own feedback
- GET /feedback - List all feedback (admin)
- GET /feedback/<id> - Get feedback details (admin)
- PATCH /feedback/<id>/status - Update status (admin)
- PATCH /feedback/<id>/priority - Update priority (admin)
- POST /feedback/<id>/respond - Add admin response (admin)
- POST /feedback/<id>/notes - Add internal note (admin)
- GET /feedback/dashboard - Dashboard stats (admin)
- POST /feedback/generate-summary - Generate AI summary batch (admin)
- GET /feedback/summaries - Get recent summaries (admin)
- GET /feedback/summaries/<id> - Get specific summary (admin)

All routes: /api/v1/feedback/*
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from datetime import datetime

from app.application.services.system.dashboard.feedback.service import FeedbackService
from app.api.middleware.auth import permission_required
from app.infrastructure.persistence.repositories.feedback.core import FeedbackRepository

feedback_bp = Blueprint('feedback', __name__, url_prefix='/feedback')

__all__ = ['feedback_bp']


# =============================================================================
# PUBLIC SUBMISSION (with optional auth)
# =============================================================================

@feedback_bp.route('/submit', methods=['POST'])
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

@feedback_bp.route('/my', methods=['GET'])
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


# =============================================================================
# ADMIN - LIST & DETAILS
# =============================================================================

@feedback_bp.route('', methods=['GET'])
@permission_required('moderation.feedback:read')
def list_feedback():
    """List all feedback with filters (admin only)."""
    feedback_type = request.args.get('type')
    status = request.args.get('status')
    priority = request.args.get('priority')
    course_id = request.args.get('course_id')
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    result = FeedbackService.get_feedback_list(
        feedback_type=feedback_type,
        status=status,
        priority=priority,
        course_id=course_id,
        search=search,
        page=page,
        per_page=min(per_page, 100)
    )

    return jsonify({
        'success': True,
        'data': result
    })


@feedback_bp.route('/<feedback_id>', methods=['GET'])
@permission_required('moderation.feedback:read')
def get_feedback(feedback_id: str):
    """Get feedback details (admin only)."""
    feedback = FeedbackService.get_feedback(feedback_id)

    if not feedback:
        return jsonify({
            'success': False,
            'error': {'code': 'NOT_FOUND', 'message': 'Feedback not found'}
        }), 404

    return jsonify({
        'success': True,
        'data': feedback
    })


# =============================================================================
# ADMIN - STATUS & PRIORITY UPDATES
# =============================================================================

@feedback_bp.route('/<feedback_id>/status', methods=['PATCH'])
@permission_required('moderation.feedback:write')
def update_status(feedback_id: str):
    """Update feedback status (admin only)."""
    data = request.get_json()
    status = data.get('status')
    admin_id = get_jwt_identity()

    if not status:
        return jsonify({
            'success': False,
            'error': {'code': 'MISSING_STATUS', 'message': 'Status is required'}
        }), 400

    feedback, error = FeedbackService.update_status(feedback_id, status, admin_id)

    if error:
        return jsonify({
            'success': False,
            'error': {'code': 'UPDATE_FAILED', 'message': error}
        }), 400

    return jsonify({
        'success': True,
        'data': feedback
    })


@feedback_bp.route('/<feedback_id>/priority', methods=['PATCH'])
@permission_required('moderation.feedback:write')
def update_priority(feedback_id: str):
    """Update feedback priority (admin only)."""
    data = request.get_json()
    priority = data.get('priority')

    if not priority:
        return jsonify({
            'success': False,
            'error': {'code': 'MISSING_PRIORITY', 'message': 'Priority is required'}
        }), 400

    feedback, error = FeedbackService.update_priority(feedback_id, priority)

    if error:
        return jsonify({
            'success': False,
            'error': {'code': 'UPDATE_FAILED', 'message': error}
        }), 400

    return jsonify({
        'success': True,
        'data': feedback
    })


# =============================================================================
# ADMIN - RESPONSES & NOTES
# =============================================================================

@feedback_bp.route('/<feedback_id>/respond', methods=['POST'])
@permission_required('moderation.feedback:write')
def respond_to_feedback(feedback_id: str):
    """Add admin response to feedback."""
    data = request.get_json()
    response = data.get('response')
    admin_id = get_jwt_identity()

    if not response:
        return jsonify({
            'success': False,
            'error': {'code': 'MISSING_RESPONSE', 'message': 'Response is required'}
        }), 400

    feedback, error = FeedbackService.respond_to_feedback(
        feedback_id=feedback_id,
        response=response,
        admin_id=admin_id
    )

    if error:
        return jsonify({
            'success': False,
            'error': {'code': 'RESPOND_FAILED', 'message': error}
        }), 400

    return jsonify({
        'success': True,
        'data': feedback
    })


@feedback_bp.route('/<feedback_id>/notes', methods=['POST'])
@permission_required('moderation.feedback:write')
def add_note(feedback_id: str):
    """Add internal note to feedback."""
    data = request.get_json()
    note_text = data.get('note')
    is_internal = data.get('is_internal', True)
    author_id = get_jwt_identity()

    if not note_text:
        return jsonify({
            'success': False,
            'error': {'code': 'MISSING_NOTE', 'message': 'Note text is required'}
        }), 400

    note, error = FeedbackService.add_note(
        feedback_id=feedback_id,
        author_id=author_id,
        note_text=note_text,
        is_internal=is_internal
    )

    if error:
        return jsonify({
            'success': False,
            'error': {'code': 'ADD_NOTE_FAILED', 'message': error}
        }), 400

    return jsonify({
        'success': True,
        'data': note
    })


# =============================================================================
# ADMIN - DASHBOARD & ANALYTICS
# =============================================================================

@feedback_bp.route('/dashboard', methods=['GET'])
@permission_required('moderation.feedback:read')
def get_dashboard():
    """Get feedback dashboard data."""
    data = FeedbackService.get_dashboard_data()

    return jsonify({
        'success': True,
        'data': data
    })


# =============================================================================
# ADMIN - AI SUMMARY BATCHES
# =============================================================================

@feedback_bp.route('/generate-summary', methods=['POST'])
@permission_required('admin.system:write')
def generate_summary():
    """Generate AI summary for feedback batch."""
    data = request.get_json() or {}

    # Optional date range
    period_start = None
    period_end = None

    if data.get('period_start'):
        try:
            period_start = datetime.fromisoformat(data['period_start'])
        except ValueError:
            pass

    if data.get('period_end'):
        try:
            period_end = datetime.fromisoformat(data['period_end'])
        except ValueError:
            pass

    batch = FeedbackService.generate_summary_batch(
        period_start=period_start,
        period_end=period_end
    )

    if not batch:
        return jsonify({
            'success': False,
            'error': {'code': 'NO_FEEDBACK', 'message': 'No feedback found in the specified period'}
        }), 404

    return jsonify({
        'success': True,
        'data': batch
    })


@feedback_bp.route('/summaries', methods=['GET'])
@permission_required('moderation.feedback:read')
def get_summaries():
    """Get recent summary batches."""
    limit = request.args.get('limit', 10, type=int)

    batches = FeedbackRepository.get_latest_summary_batches(min(limit, 50))

    return jsonify({
        'success': True,
        'data': {
            'batches': batches
        }
    })


@feedback_bp.route('/summaries/<batch_id>', methods=['GET'])
@permission_required('moderation.feedback:read')
def get_summary(batch_id: str):
    """Get a specific summary batch."""
    batch = FeedbackRepository.get_summary_batch_by_id(batch_id)

    if not batch:
        return jsonify({
            'success': False,
            'error': {'code': 'NOT_FOUND', 'message': 'Summary batch not found'}
        }), 404

    return jsonify({
        'success': True,
        'data': batch
    })
