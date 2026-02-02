"""
LernsystemX Analytics API - Consolidated

System-wide analytics tracking and reporting.

User Analytics:
- POST /analytics/event - Track analytics event
- GET /analytics/user - Get user statistics
- GET /analytics/organisation - Get organisation statistics
- GET /analytics/health - Analytics system health check

Admin Analytics:
- GET /admin/analytics/events/time-series - System-wide events time series
- GET /admin/analytics/active-users/time-series - System-wide active users time series

All routes: /api/v1/analytics/*, /api/v1/admin/analytics/*
ISO 27001:2013 compliant - Analytics & Reporting Layer
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
import logging

from app.core.bootstrap.extensions import limiter
from app.api.middleware.auth import token_required, get_current_user, permission_required
from app.domain.models.analytics import (
    AnalyticsEventCreateRequest,
    AnalyticsEventResponse,
    AnalyticsUserStats,
    AnalyticsOrgStats,
    AnalyticsStatsResponse,
    TimeSeriesResponse,
    TimeSeriesDataPoint
)
from app.application.services.analytics.service import AnalyticsService
from app.infrastructure.persistence.repositories.analytics import AnalyticsRepository

# Blueprints
analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')
analytics_admin_bp = Blueprint('analytics_admin', __name__, url_prefix='/admin-panel/analytics')

__all__ = ['analytics_bp', 'analytics_admin_bp']

logger = logging.getLogger(__name__)


# =============================================================================
# HELPER FUNCTIONS (INLINE)
# =============================================================================

def parse_date_range(range_param: str) -> Tuple[datetime, datetime]:
    """Parse range parameter to from_date and to_date."""
    range_map = {'7d': 7, '30d': 30, '90d': 90}
    days = range_map.get(range_param, 7)
    to_date = datetime.utcnow()
    from_date = to_date - timedelta(days=days)
    return from_date, to_date


# =============================================================================
# USER ANALYTICS ENDPOINTS
# =============================================================================

@analytics_bp.route('/event', methods=['POST'])
@token_required
def track_event():
    """
    Track analytics event.

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
    """
    try:
        from pydantic import ValidationError

        user = get_current_user()
        data = request.get_json()

        # Validate request body
        event_request = AnalyticsEventCreateRequest(**data)

        # Get IP address from request
        ip_address = request.remote_addr

        # Track event
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


@analytics_bp.route('/user', methods=['GET'])
@token_required
def get_user_analytics():
    """
    Get user analytics statistics.

    Response:
        200: User statistics
        {
            "success": true,
            "stats_type": "user",
            "stats": {
                "user_id": 123,
                "total_events": 150,
                "event_counts_by_type": {...},
                "recent_events": [...],
                "courses_viewed": 50,
                "courses_enrolled": 15,
                "modules_completed": 10
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


@analytics_bp.route('/organisation', methods=['GET'])
@token_required
def get_organisation_analytics():
    """
    Get organisation analytics statistics.

    Requires: Teacher, School Admin, Company Admin, Admin, or Superadmin

    Response:
        200: Organisation statistics
        403: Forbidden (insufficient permissions)
        500: Server error
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


@analytics_bp.route('/health', methods=['GET'])
def analytics_health():
    """
    Analytics system health check.

    Public endpoint to verify analytics system is operational.

    Response:
        200: System healthy
    """
    return jsonify({
        'success': True,
        'message': 'Analytics system operational',
        'version': '1.0.0'
    }), 200


# =============================================================================
# ADMIN ANALYTICS ENDPOINTS
# =============================================================================

@analytics_admin_bp.route('/events/time-series', methods=['GET'])
@permission_required('admin.analytics:read')
@limiter.limit("60 per minute")
def get_events_time_series() -> Tuple[Dict[str, Any], int]:
    """
    Get system-wide events time series.

    Query Parameters:
        range (str): Time range - '7d', '30d', '90d' (default: 7d)
        from (str): Start date (YYYY-MM-DD) - overrides range
        to (str): End date (YYYY-MM-DD) - overrides range

    Response:
        200: Time series data
        {
            "success": true,
            "data": [
                {"date": "2025-01-15", "value": 42},
                {"date": "2025-01-16", "value": 58}
            ],
            "total": 100
        }

    Security:
        Requires: VIEW_SYSTEM_ANALYTICS permission (admin, superadmin)
    """
    try:
        # Parse query parameters
        range_param = request.args.get('range', '7d')
        from_str = request.args.get('from')
        to_str = request.args.get('to')

        # Determine date range
        if from_str and to_str:
            from_date = datetime.strptime(from_str, '%Y-%m-%d')
            to_date = datetime.strptime(to_str, '%Y-%m-%d')
        else:
            from_date, to_date = parse_date_range(range_param)

        # Fetch time series from repository
        raw_data = AnalyticsRepository.get_events_time_series(
            from_date=from_date,
            to_date=to_date
        )

        # Transform to response model
        data_points = []
        total = 0
        for row in raw_data:
            point = TimeSeriesDataPoint(
                date=str(row['date']),
                value=row['count']
            )
            data_points.append(point)
            total += point.value

        # Build response using Pydantic model
        response = TimeSeriesResponse(
            success=True,
            data=data_points,
            total=total
        )

        return jsonify(response.model_dump()), 200

    except ValueError as ve:
        logger.warning(f"Invalid parameters for events time series: {ve}")
        return jsonify({
            'success': False,
            'error': 'Invalid parameters',
            'message': str(ve)
        }), 400

    except Exception as e:
        logger.error(f"Error fetching events time series: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch events time series',
            'details': str(e)
        }), 500


@analytics_admin_bp.route('/active-users/time-series', methods=['GET'])
@permission_required('admin.analytics:read')
@limiter.limit("60 per minute")
def get_active_users_time_series() -> Tuple[Dict[str, Any], int]:
    """
    Get system-wide active users time series.

    Query Parameters:
        range (str): Time range - '7d', '30d', '90d' (default: 7d)
        from (str): Start date (YYYY-MM-DD)
        to (str): End date (YYYY-MM-DD)

    Response:
        200: Time series data
        {
            "success": true,
            "data": [
                {"date": "2025-01-15", "value": 12},
                {"date": "2025-01-16", "value": 15}
            ],
            "total": 27
        }

    Security:
        Requires: VIEW_SYSTEM_ANALYTICS permission
    """
    try:
        # Parse query parameters
        range_param = request.args.get('range', '7d')
        from_str = request.args.get('from')
        to_str = request.args.get('to')

        # Determine date range
        if from_str and to_str:
            from_date = datetime.strptime(from_str, '%Y-%m-%d')
            to_date = datetime.strptime(to_str, '%Y-%m-%d')
        else:
            from_date, to_date = parse_date_range(range_param)

        # Fetch time series from repository
        raw_data = AnalyticsRepository.get_active_users_time_series(
            from_date=from_date,
            to_date=to_date
        )

        # Transform to response model
        data_points = []
        for row in raw_data:
            point = TimeSeriesDataPoint(
                date=str(row['date']),
                value=row['count']
            )
            data_points.append(point)

        # Total unique users (max daily count)
        total = max((point.value for point in data_points), default=0)

        # Build response using Pydantic model
        response = TimeSeriesResponse(
            success=True,
            data=data_points,
            total=total
        )

        return jsonify(response.model_dump()), 200

    except ValueError as ve:
        logger.warning(f"Invalid parameters for active users time series: {ve}")
        return jsonify({
            'success': False,
            'error': 'Invalid parameters',
            'message': str(ve)
        }), 400

    except Exception as e:
        logger.error(f"Error fetching active users time series: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch active users time series',
            'details': str(e)
        }), 500
