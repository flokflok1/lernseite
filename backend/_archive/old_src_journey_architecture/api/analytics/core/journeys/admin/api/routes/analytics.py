"""
Admin Analytics Routes (Journey-Based API)

Admin journey for analytics and feedback management.
ALL data loaded dynamically from database - NO hardcoded values.

Endpoints:
- GET /api/v1/admin/analytics/sessions - List sessions
- GET /api/v1/admin/analytics/sessions/<id> - Get session details
- GET /api/v1/admin/analytics/events - List events
- GET /api/v1/admin/analytics/aggregates - Get aggregates
- GET /api/v1/admin/feedback - List feedback
- GET /api/v1/admin/feedback/<id> - Get feedback details
- POST /api/v1/admin/feedback - Create feedback (admin on behalf)
- PUT /api/v1/admin/feedback/<id>/status - Update status
- PUT /api/v1/admin/feedback/<id>/respond - Add admin response
- GET /api/v1/admin/feedback/<id>/attachments - Get attachments
- POST /api/v1/admin/feedback/<id>/attachments - Add attachment
- GET /api/v1/admin/feedback/<id>/notes - Get notes
- POST /api/v1/admin/feedback/<id>/notes - Add note
"""

from flask import Blueprint, request, jsonify
from datetime import date, datetime
from decimal import Decimal
from src.core.auth.permissions import require_auth, require_role
from src.api.analytics.core.application.services.analytics_service import AnalyticsService
from src.core.utils.validators import Validators, ValidationError


# Create blueprint
admin_analytics_bp = Blueprint('admin_analytics', __name__)


# ============================================================================
# ANALYTICS SESSIONS
# ============================================================================

@admin_analytics_bp.route('/api/v1/admin/analytics/sessions', methods=['GET'])
@require_auth
@require_role(['admin', 'moderator'])
def list_analytics_sessions():
    """List analytics sessions with filters."""
    try:
        # TODO: Add filters (user_id, date range, device_type)
        # For now, return empty list as this needs additional repository methods
        return jsonify({
            'success': True,
            'data': [],
            'meta': {'message': 'Session listing with filters - coming soon'}
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'LIST_SESSIONS_ERROR', 'message': str(e)}}), 500


@admin_analytics_bp.route('/api/v1/admin/analytics/sessions/<session_id>', methods=['GET'])
@require_auth
@require_role(['admin', 'moderator'])
def get_analytics_session(session_id: str):
    """Get analytics session details by ID."""
    try:
        Validators.validate_uuid(session_id)
        session = AnalyticsService.get_session_by_id(session_id)

        if not session:
            return jsonify({'success': False, 'error': {'code': 'SESSION_NOT_FOUND', 'message': f'Session {session_id} not found'}}), 404

        session_data = {
            'session_id': session.session_id,
            'user_id': session.user_id,
            'organization_id': session.organization_id,
            'device_type': session.device_type,
            'browser': session.browser,
            'os': session.os,
            'country': session.country,
            'city': session.city,
            'started_at': session.started_at.isoformat() if session.started_at else None,
            'ended_at': session.ended_at.isoformat() if session.ended_at else None,
            'duration_seconds': session.duration_seconds,
            'duration_minutes': session.get_duration_minutes(),
            'page_views': session.page_views,
            'is_active': session.is_active()
        }

        return jsonify({'success': True, 'data': session_data}), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'GET_SESSION_ERROR', 'message': str(e)}}), 500


# ============================================================================
# ANALYTICS EVENTS
# ============================================================================

@admin_analytics_bp.route('/api/v1/admin/analytics/events', methods=['GET'])
@require_auth
@require_role(['admin', 'moderator'])
def list_analytics_events():
    """List analytics events with filters."""
    try:
        user_id = request.args.get('user_id')
        event_type = request.args.get('event_type')
        limit = request.args.get('limit', 100, type=int)

        if not user_id:
            return jsonify({'success': False, 'error': {'code': 'MISSING_USER_ID', 'message': 'user_id parameter required'}}), 400

        Validators.validate_uuid(user_id)

        events = AnalyticsService.get_events_by_user(user_id, event_type, limit)

        events_data = [
            {
                'event_id': e.event_id,
                'event_type': e.event_type,
                'event_category': e.event_category,
                'resource_type': e.resource_type,
                'resource_id': e.resource_id,
                'payload': e.payload,
                'session_id': e.session_id,
                'created_at': e.created_at.isoformat() if e.created_at else None,
                'is_user_action': e.is_user_action(),
                'is_completion': e.is_completion_event()
            }
            for e in events
        ]

        return jsonify({
            'success': True,
            'data': events_data,
            'meta': {'count': len(events_data), 'limit': limit}
        }), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'LIST_EVENTS_ERROR', 'message': str(e)}}), 500


# ============================================================================
# ANALYTICS AGGREGATES
# ============================================================================

@admin_analytics_bp.route('/api/v1/admin/analytics/aggregates', methods=['GET'])
@require_auth
@require_role(['admin', 'moderator'])
def get_analytics_aggregates():
    """
    Get analytics aggregates.

    Query params:
    - metric_type: required
    - start_date: required (YYYY-MM-DD)
    - end_date: required (YYYY-MM-DD)
    - dimension: optional
    - dimension_value: optional
    """
    try:
        metric_type = request.args.get('metric_type')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        dimension = request.args.get('dimension')
        dimension_value = request.args.get('dimension_value')

        if not metric_type or not start_date_str or not end_date_str:
            return jsonify({'success': False, 'error': {'code': 'MISSING_PARAMS', 'message': 'metric_type, start_date, end_date required'}}), 400

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        aggregates = AnalyticsService.get_aggregates(
            metric_type, start_date, end_date, dimension, dimension_value
        )

        aggregates_data = [
            {
                'aggregate_id': a.aggregate_id,
                'metric_type': a.metric_type,
                'dimension': a.dimension,
                'dimension_value': a.dimension_value,
                'date': a.date.isoformat(),
                'hour': a.hour,
                'value': float(a.value),
                'count': a.count,
                'average_value': float(a.get_average_value()) if a.get_average_value() else None,
                'is_hourly': a.is_hourly(),
                'metadata': a.metadata
            }
            for a in aggregates
        ]

        return jsonify({
            'success': True,
            'data': aggregates_data,
            'meta': {'count': len(aggregates_data), 'metric_type': metric_type}
        }), 200

    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_DATE', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'GET_AGGREGATES_ERROR', 'message': str(e)}}), 500


# ============================================================================
# USER FEEDBACK
# ============================================================================

@admin_analytics_bp.route('/api/v1/admin/feedback', methods=['GET'])
@require_auth
@require_role(['admin', 'moderator', 'support'])
def list_feedback():
    """
    List all feedback with filters.

    Query params:
    - status: Filter by status (new, read, in_progress, resolved, closed)
    - feedback_type: Filter by type (question, bug, suggestion, praise, other)
    - priority: Filter by priority (low, normal, high, urgent)
    - limit: Result limit (default: 100)
    - offset: Result offset (default: 0)
    """
    try:
        status = request.args.get('status')
        feedback_type = request.args.get('feedback_type')
        priority = request.args.get('priority')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)

        feedback_list = AnalyticsService.get_all_feedback(
            status, feedback_type, priority, limit, offset
        )

        feedback_data = [
            {
                'feedback_id': f.feedback_id,
                'user_id': f.user_id,
                'is_anonymous': f.is_anonymous,
                'email': f.email,
                'feedback_type': f.feedback_type,
                'title': f.title,
                'message': f.message,
                'status': f.status,
                'priority': f.priority,
                'assigned_to': f.assigned_to,
                'ai_sentiment': f.ai_sentiment,
                'ai_category': f.ai_category,
                'has_response': f.has_admin_response(),
                'created_at': f.created_at.isoformat() if f.created_at else None,
                'resolved_at': f.resolved_at.isoformat() if f.resolved_at else None
            }
            for f in feedback_list
        ]

        return jsonify({
            'success': True,
            'data': feedback_data,
            'meta': {'count': len(feedback_data), 'limit': limit, 'offset': offset}
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'LIST_FEEDBACK_ERROR', 'message': str(e)}}), 500


@admin_analytics_bp.route('/api/v1/admin/feedback/<feedback_id>', methods=['GET'])
@require_auth
@require_role(['admin', 'moderator', 'support'])
def get_feedback(feedback_id: str):
    """Get feedback details by ID."""
    try:
        Validators.validate_uuid(feedback_id)
        feedback = AnalyticsService.get_feedback_by_id(feedback_id)

        if not feedback:
            return jsonify({'success': False, 'error': {'code': 'FEEDBACK_NOT_FOUND', 'message': f'Feedback {feedback_id} not found'}}), 404

        feedback_data = {
            'feedback_id': feedback.feedback_id,
            'user_id': feedback.user_id,
            'is_anonymous': feedback.is_anonymous,
            'email': feedback.email,
            'feedback_type': feedback.feedback_type,
            'title': feedback.title,
            'message': feedback.message,
            'context_course_id': feedback.context_course_id,
            'context_lesson_id': feedback.context_lesson_id,
            'context_page': feedback.context_page,
            'context_url': feedback.context_url,
            'context_data': feedback.context_data,
            'status': feedback.status,
            'priority': feedback.priority,
            'assigned_to': feedback.assigned_to,
            'ai_summary': feedback.ai_summary,
            'ai_category': feedback.ai_category,
            'ai_sentiment': feedback.ai_sentiment,
            'ai_tags': feedback.ai_tags,
            'ai_processed_at': feedback.ai_processed_at.isoformat() if feedback.ai_processed_at else None,
            'admin_response': feedback.admin_response,
            'admin_responded_by': feedback.admin_responded_by,
            'admin_responded_at': feedback.admin_responded_at.isoformat() if feedback.admin_responded_at else None,
            'created_at': feedback.created_at.isoformat() if feedback.created_at else None,
            'updated_at': feedback.updated_at.isoformat() if feedback.updated_at else None,
            'resolved_at': feedback.resolved_at.isoformat() if feedback.resolved_at else None
        }

        return jsonify({'success': True, 'data': feedback_data}), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'GET_FEEDBACK_ERROR', 'message': str(e)}}), 500


@admin_analytics_bp.route('/api/v1/admin/feedback/<feedback_id>/status', methods=['PUT'])
@require_auth
@require_role(['admin', 'moderator', 'support'])
def update_feedback_status(feedback_id: str):
    """Update feedback status and assignment."""
    try:
        Validators.validate_uuid(feedback_id)
        data = request.get_json()

        if not data or 'status' not in data:
            return jsonify({'success': False, 'error': {'code': 'MISSING_STATUS', 'message': 'status field required'}}), 400

        status = data['status']
        assigned_to = data.get('assigned_to')
        admin_id = request.current_user.get('user_id')  # From auth middleware

        updated_feedback = AnalyticsService.update_feedback_status(
            feedback_id, status, assigned_to, admin_id
        )

        return jsonify({
            'success': True,
            'data': {
                'feedback_id': updated_feedback.feedback_id,
                'status': updated_feedback.status,
                'assigned_to': updated_feedback.assigned_to,
                'updated_at': updated_feedback.updated_at.isoformat() if updated_feedback.updated_at else None
            }
        }), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_DATA', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'UPDATE_STATUS_ERROR', 'message': str(e)}}), 500


@admin_analytics_bp.route('/api/v1/admin/feedback/<feedback_id>/respond', methods=['PUT'])
@require_auth
@require_role(['admin', 'moderator', 'support'])
def respond_to_feedback(feedback_id: str):
    """Add admin response to feedback."""
    try:
        Validators.validate_uuid(feedback_id)
        data = request.get_json()

        if not data or 'response' not in data:
            return jsonify({'success': False, 'error': {'code': 'MISSING_RESPONSE', 'message': 'response field required'}}), 400

        response = data['response']
        admin_id = request.current_user.get('user_id')  # From auth middleware

        updated_feedback = AnalyticsService.add_admin_response(feedback_id, response, admin_id)

        return jsonify({
            'success': True,
            'data': {
                'feedback_id': updated_feedback.feedback_id,
                'admin_response': updated_feedback.admin_response,
                'admin_responded_by': updated_feedback.admin_responded_by,
                'admin_responded_at': updated_feedback.admin_responded_at.isoformat() if updated_feedback.admin_responded_at else None
            }
        }), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_DATA', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'RESPOND_ERROR', 'message': str(e)}}), 500


# ============================================================================
# FEEDBACK ATTACHMENTS
# ============================================================================

@admin_analytics_bp.route('/api/v1/admin/feedback/<feedback_id>/attachments', methods=['GET'])
@require_auth
@require_role(['admin', 'moderator', 'support'])
def get_feedback_attachments(feedback_id: str):
    """Get all attachments for a feedback."""
    try:
        Validators.validate_uuid(feedback_id)
        attachments = AnalyticsService.get_feedback_attachments(feedback_id)

        attachments_data = [
            {
                'attachment_id': a.attachment_id,
                'file_name': a.file_name,
                'file_type': a.file_type,
                'file_size': a.file_size,
                'file_size_mb': a.get_file_size_mb(),
                'is_screenshot': a.is_screenshot,
                'ai_screenshot_description': a.ai_screenshot_description,
                'created_at': a.created_at.isoformat() if a.created_at else None
            }
            for a in attachments
        ]

        return jsonify({
            'success': True,
            'data': attachments_data,
            'meta': {'count': len(attachments_data)}
        }), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'GET_ATTACHMENTS_ERROR', 'message': str(e)}}), 500


# ============================================================================
# FEEDBACK NOTES
# ============================================================================

@admin_analytics_bp.route('/api/v1/admin/feedback/<feedback_id>/notes', methods=['GET'])
@require_auth
@require_role(['admin', 'moderator', 'support'])
def get_feedback_notes(feedback_id: str):
    """Get all notes for a feedback."""
    try:
        Validators.validate_uuid(feedback_id)
        notes = AnalyticsService.get_feedback_notes(feedback_id)

        notes_data = [
            {
                'note_id': n.note_id,
                'author_id': n.author_id,
                'note_text': n.note_text,
                'is_internal': n.is_internal,
                'word_count': n.get_word_count(),
                'created_at': n.created_at.isoformat() if n.created_at else None
            }
            for n in notes
        ]

        return jsonify({
            'success': True,
            'data': notes_data,
            'meta': {'count': len(notes_data)}
        }), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'GET_NOTES_ERROR', 'message': str(e)}}), 500


@admin_analytics_bp.route('/api/v1/admin/feedback/<feedback_id>/notes', methods=['POST'])
@require_auth
@require_role(['admin', 'moderator', 'support'])
def add_feedback_note(feedback_id: str):
    """Add note to feedback."""
    try:
        Validators.validate_uuid(feedback_id)
        data = request.get_json()

        if not data or 'note_text' not in data:
            return jsonify({'success': False, 'error': {'code': 'MISSING_NOTE', 'message': 'note_text field required'}}), 400

        note_text = data['note_text']
        is_internal = data.get('is_internal', True)
        author_id = request.current_user.get('user_id')  # From auth middleware

        created_note = AnalyticsService.add_feedback_note(
            feedback_id, author_id, note_text, is_internal
        )

        return jsonify({
            'success': True,
            'data': {
                'note_id': created_note.note_id,
                'feedback_id': created_note.feedback_id,
                'author_id': created_note.author_id,
                'note_text': created_note.note_text,
                'is_internal': created_note.is_internal,
                'created_at': created_note.created_at.isoformat() if created_note.created_at else None
            }
        }), 201

    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'ADD_NOTE_ERROR', 'message': str(e)}}), 500
