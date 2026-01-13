"""
Feedback Admin Management - Admin endpoints for feedback system.

Endpoints:
- GET /feedback - List all feedback
- GET /feedback/<id> - Get feedback details
- PATCH /feedback/<id>/status - Update status
- PATCH /feedback/<id>/priority - Update priority
- POST /feedback/<id>/respond - Add admin response
- POST /feedback/<id>/notes - Add internal note
- GET /feedback/dashboard - Dashboard stats
- POST /feedback/generate-summary - Generate AI summary batch
- GET /feedback/summaries - Get recent summaries
- GET /feedback/summaries/<id> - Get specific summary
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from app.services.feedback_service import FeedbackService
from app.middleware.auth import role_required
from app.repositories.feedback.core import FeedbackRepository

bp = Blueprint('feedback_admin', __name__)


# =============================================================================
# LIST & DETAILS
# =============================================================================

@bp.route('', methods=['GET'])
@jwt_required()
@role_required(['admin', 'moderator', 'support'])
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


@bp.route('/<feedback_id>', methods=['GET'])
@jwt_required()
@role_required(['admin', 'moderator', 'support'])
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
# STATUS & PRIORITY UPDATES
# =============================================================================

@bp.route('/<feedback_id>/status', methods=['PATCH'])
@jwt_required()
@role_required(['admin', 'moderator', 'support'])
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


@bp.route('/<feedback_id>/priority', methods=['PATCH'])
@jwt_required()
@role_required(['admin', 'moderator', 'support'])
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
# RESPONSES & NOTES
# =============================================================================

@bp.route('/<feedback_id>/respond', methods=['POST'])
@jwt_required()
@role_required(['admin', 'moderator', 'support'])
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


@bp.route('/<feedback_id>/notes', methods=['POST'])
@jwt_required()
@role_required(['admin', 'moderator', 'support'])
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
# DASHBOARD & ANALYTICS
# =============================================================================

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
@role_required(['admin', 'moderator', 'support'])
def get_dashboard():
    """Get feedback dashboard data."""
    data = FeedbackService.get_dashboard_data()

    return jsonify({
        'success': True,
        'data': data
    })


# =============================================================================
# AI SUMMARY BATCHES
# =============================================================================

@bp.route('/generate-summary', methods=['POST'])
@jwt_required()
@role_required(['admin'])
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


@bp.route('/summaries', methods=['GET'])
@jwt_required()
@role_required(['admin', 'moderator'])
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


@bp.route('/summaries/<batch_id>', methods=['GET'])
@jwt_required()
@role_required(['admin', 'moderator'])
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
