"""
LernsystemX Analytics API

Analytics event tracking and statistics endpoints:
- POST  /api/v1/analytics/event - Track analytics event
- GET   /api/v1/analytics/user - Get user statistics
- GET   /api/v1/analytics/organisation - Get organisation statistics

ISO 27001:2013 compliant - Analytics tracking
"""

from flask import request, jsonify
from pydantic import ValidationError

from app.api import api_v1
from app.models.analytics import (
    AnalyticsEventCreateRequest,
    AnalyticsEventResponse,
    AnalyticsUserStats,
    AnalyticsOrgStats,
    AnalyticsStatsResponse
)
from app.services.analytics_service import AnalyticsService
from app.middleware.auth import token_required, get_current_user


@api_v1.route('/analytics/event', methods=['POST'])
@token_required
def track_event():
    """
    Track analytics event

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "event_type": "course_view",
            "resource_type": "course",
            "resource_id": 42,
            "payload": {"duration_seconds": 120},
            "session_id": "abc123"
        }

    Response:
        200: Event tracked successfully
        400: Validation error
        401: Unauthorized
        500: Server error

    Example Response:
        {
            "success": true,
            "message": "Event tracked successfully",
            "event": {
                "event_id": 12345,
                "user_id": 123,
                "event_type": "course_view",
                "resource_type": "course",
                "resource_id": 42,
                "payload": {"duration_seconds": 120},
                "created_at": "2025-11-16T20:00:00Z"
            }
        }
    """
    try:
        user = get_current_user()
        data = request.get_json()

        # Validate request body
        event_request = AnalyticsEventCreateRequest(**data)

        # Get IP address from request
        ip_address = request.remote_addr

        # Track event
        # Convert enum to string value for service layer
        event_type_str = event_request.event_type.value if hasattr(event_request.event_type, 'value') else str(event_request.event_type)
        resource_type_str = event_request.resource_type.value if event_request.resource_type and hasattr(event_request.resource_type, 'value') else (str(event_request.resource_type) if event_request.resource_type else None)

        event = AnalyticsService.track_event(
            user=user,
            event_type=event_type_str,
            resource_type=resource_type_str,
            resource_id=event_request.resource_id,
            payload=event_request.payload,
            session_id=event_request.session_id,
            ip_address=ip_address
        )

        return jsonify({
            'success': True,
            'message': 'Event tracked successfully',
            'event': event.model_dump()
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid request',
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to track event',
            'details': str(e)
        }), 500


@api_v1.route('/analytics/user', methods=['GET'])
@token_required
def get_user_analytics():
    """
    Get user analytics statistics

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: User statistics
        401: Unauthorized
        500: Server error

    Example Response:
        {
            "success": true,
            "stats_type": "user",
            "stats": {
                "user_id": 123,
                "total_events": 150,
                "event_counts_by_type": {
                    "login": 25,
                    "course_view": 50,
                    "module_complete": 10
                },
                "recent_events": [...],
                "first_event_at": "2025-01-01T10:00:00Z",
                "last_event_at": "2025-11-16T20:00:00Z",
                "courses_viewed": 50,
                "courses_enrolled": 15,
                "modules_completed": 10,
                "lessons_completed": 45
            }
        }
    """
    try:
        user = get_current_user()

        # Get user statistics
        stats = AnalyticsService.get_user_statistics(user)

        return jsonify({
            'success': True,
            'stats_type': 'user',
            'stats': stats.model_dump()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get user analytics',
            'details': str(e)
        }), 500


@api_v1.route('/analytics/organisation', methods=['GET'])
@token_required
def get_organisation_analytics():
    """
    Get organisation analytics statistics

    Requires: Teacher, School Admin, Company Admin, Admin, or Superadmin

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Organisation statistics
        401: Unauthorized
        403: Forbidden (insufficient permissions)
        500: Server error

    Example Response:
        {
            "success": true,
            "stats_type": "organisation",
            "stats": {
                "organisation_id": 5,
                "total_events": 5000,
                "total_users": 150,
                "active_users_30d": 85,
                "event_counts_by_type": {
                    "login": 850,
                    "course_view": 1200,
                    "module_complete": 450
                },
                "top_courses": [
                    {"course_id": 10, "event_count": 320},
                    {"course_id": 15, "event_count": 280}
                ],
                "first_event_at": "2024-09-01T08:00:00Z",
                "last_event_at": "2025-11-16T20:00:00Z",
                "total_course_enrollments": 450,
                "total_modules_completed": 1200,
                "total_exams_completed": 95,
                "avg_completion_rate": 78.5
            }
        }
    """
    try:
        user = get_current_user()

        # Get organisation statistics
        stats = AnalyticsService.get_organisation_statistics(user)

        return jsonify({
            'success': True,
            'stats_type': 'organisation',
            'stats': stats.model_dump()
        }), 200

    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': str(e)
        }), 403

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid request',
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get organisation analytics',
            'details': str(e)
        }), 500


@api_v1.route('/analytics/health', methods=['GET'])
def analytics_health():
    """
    Analytics system health check

    Public endpoint to verify analytics system is operational

    Response:
        200: System healthy
        {
            "success": true,
            "message": "Analytics system operational",
            "version": "1.0.0"
        }
    """
    return jsonify({
        'success': True,
        'message': 'Analytics system operational',
        'version': '1.0.0'
    }), 200
