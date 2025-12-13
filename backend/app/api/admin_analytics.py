"""
LernsystemX Admin Analytics API

Advanced analytics endpoints for system administrators:
- GET /api/v1/admin/analytics/events/time-series - System-wide events time series
- GET /api/v1/admin/analytics/active-users/time-series - Active users time series
- GET /api/v1/admin/analytics/top-courses - Top courses by activity
- GET /api/v1/admin/analytics/top-methods - Top learning methods by usage

Phase B10 - ISO 27001:2013 compliant
"""

from flask import request, jsonify, current_app
from datetime import datetime, timedelta
import traceback

from app.api import api_v1
from app.models.analytics import (
    TimeSeriesResponse,
    TimeSeriesDataPoint,
    TopCoursesResponse,
    TopCourseAnalytics,
    TopMethodsResponse,
    TopMethodAnalytics
)
from app.repositories.analytics_repository import AnalyticsRepository
from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions


def parse_date_range(range_param: str):
    """
    Parse range parameter to from_date and to_date

    Args:
        range_param: '7d', '30d', or '90d'

    Returns:
        tuple: (from_date, to_date)
    """
    range_map = {
        '7d': 7,
        '30d': 30,
        '90d': 90
    }

    days = range_map.get(range_param, 7)
    to_date = datetime.utcnow()
    from_date = to_date - timedelta(days=days)

    return from_date, to_date


@api_v1.route('/admin/analytics/events/time-series', methods=['GET'])
@token_required
@require_permission(Permissions.VIEW_SYSTEM_ANALYTICS)
def admin_get_events_time_series():
    """
    Get system-wide events time series

    Query Parameters:
        range: Time range - '7d', '30d', '90d' (default: 7d)
        from: Start date (YYYY-MM-DD) - overrides range
        to: End date (YYYY-MM-DD) - overrides range

    Response:
        200: Time series data
        {
            "success": true,
            "data": [
                {"date": "2025-01-15", "value": 245},
                {"date": "2025-01-16", "value": 312}
            ],
            "total": 557
        }

        401: Unauthorized
        403: Forbidden (requires VIEW_SYSTEM_ANALYTICS permission)
        500: Server error

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
        raw_data = AnalyticsRepository.get_events_time_series(from_date, to_date)

        # Transform to response model
        data_points = [
            TimeSeriesDataPoint(
                date=str(row['date']),
                value=row['count']
            )
            for row in raw_data
        ]

        total = sum(point.value for point in data_points)

        response = TimeSeriesResponse(
            success=True,
            data=data_points,
            total=total
        )

        return jsonify(response.model_dump()), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid date format',
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch events time series',
            'details': str(e)
        }), 500


@api_v1.route('/admin/analytics/active-users/time-series', methods=['GET'])
@token_required
@require_permission(Permissions.VIEW_SYSTEM_ANALYTICS)
def admin_get_active_users_time_series():
    """
    Get system-wide active users time series

    Query Parameters:
        range: Time range - '7d', '30d', '90d' (default: 7d)
        from: Start date (YYYY-MM-DD)
        to: End date (YYYY-MM-DD)

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

        401: Unauthorized
        403: Forbidden
        500: Server error

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
        raw_data = AnalyticsRepository.get_active_users_time_series(from_date, to_date)

        # Transform to response model
        data_points = [
            TimeSeriesDataPoint(
                date=str(row['date']),
                value=row['count']
            )
            for row in raw_data
        ]

        # Total unique users across entire period (max of daily counts)
        total = max((point.value for point in data_points), default=0)

        response = TimeSeriesResponse(
            success=True,
            data=data_points,
            total=total
        )

        return jsonify(response.model_dump()), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid date format',
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch active users time series',
            'details': str(e)
        }), 500


@api_v1.route('/admin/analytics/top-courses', methods=['GET'])
@token_required
@require_permission(Permissions.VIEW_SYSTEM_ANALYTICS)
def admin_get_top_courses():
    """
    Get top courses by activity

    Query Parameters:
        limit: Number of top courses (default: 10, max: 100)
        range: Time range - '7d', '30d', '90d'
        from: Start date (YYYY-MM-DD)
        to: End date (YYYY-MM-DD)

    Response:
        200: Top courses data
        {
            "success": true,
            "courses": [
                {
                    "course_id": 42,
                    "title": "Python for Beginners",
                    "events_count": 1250,
                    "enrollments": 145,
                    "completions": 67,
                    "avg_completion_rate": 46.2
                }
            ],
            "total": 10
        }

        401: Unauthorized
        403: Forbidden
        500: Server error

    Security:
        Requires: VIEW_SYSTEM_ANALYTICS permission
    """
    try:
        # Parse query parameters
        limit = min(int(request.args.get('limit', 10)), 100)
        range_param = request.args.get('range')
        days_param = request.args.get('days')  # Support legacy 'days' parameter
        from_str = request.args.get('from')
        to_str = request.args.get('to')

        # Determine date range
        from_date, to_date = None, None
        if from_str and to_str:
            from_date = datetime.strptime(from_str, '%Y-%m-%d')
            to_date = datetime.strptime(to_str, '%Y-%m-%d')
        elif range_param:
            from_date, to_date = parse_date_range(range_param)
        elif days_param:
            # Convert days parameter to range format (e.g., days=7 -> '7d')
            from_date, to_date = parse_date_range(f'{days_param}d')

        # Fetch top courses from repository
        raw_data = AnalyticsRepository.get_top_courses(
            limit=limit,
            from_date=from_date,
            to_date=to_date
        )

        # Transform to response model
        courses = [
            TopCourseAnalytics(
                course_id=row['course_id'],
                title=row['title'] or f"Course {row['course_id']}",
                events_count=row['events_count'],
                enrollments=row['enrollments'],
                completions=row['completions'],
                avg_completion_rate=(
                    (row['completions'] / row['enrollments'] * 100)
                    if row['enrollments'] > 0
                    else 0.0
                )
            )
            for row in raw_data
        ]

        response = TopCoursesResponse(
            success=True,
            courses=courses,
            total=len(courses)
        )

        return jsonify(response.model_dump()), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid parameter',
            'message': str(e)
        }), 400

    except Exception as e:
        current_app.logger.error(f"ERROR in admin_get_top_courses: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Failed to fetch top courses',
            'details': str(e)
        }), 500


@api_v1.route('/admin/analytics/top-methods', methods=['GET'])
@token_required
@require_permission(Permissions.VIEW_SYSTEM_ANALYTICS)
def admin_get_top_methods():
    """
    Get top learning methods by usage

    Query Parameters:
        limit: Number of top methods (default: 10, max: 100)
        range: Time range - '7d', '30d', '90d'
        from: Start date (YYYY-MM-DD)
        to: End date (YYYY-MM-DD)

    Response:
        200: Top methods data
        {
            "success": true,
            "methods": [
                {
                    "method_id": 5,
                    "name": "Flashcards",
                    "calls": 2450,
                    "tokens_used": 125000,
                    "avg_tokens": 51
                }
            ],
            "total": 10
        }

        401: Unauthorized
        403: Forbidden
        500: Server error

    Security:
        Requires: VIEW_SYSTEM_ANALYTICS permission
    """
    try:
        # Parse query parameters
        limit = min(int(request.args.get('limit', 10)), 100)
        range_param = request.args.get('range')
        days_param = request.args.get('days')  # Support legacy 'days' parameter
        from_str = request.args.get('from')
        to_str = request.args.get('to')

        # Determine date range
        from_date, to_date = None, None
        if from_str and to_str:
            from_date = datetime.strptime(from_str, '%Y-%m-%d')
            to_date = datetime.strptime(to_str, '%Y-%m-%d')
        elif range_param:
            from_date, to_date = parse_date_range(range_param)
        elif days_param:
            # Convert days parameter to range format (e.g., days=7 -> '7d')
            from_date, to_date = parse_date_range(f'{days_param}d')

        # Fetch top methods from repository
        raw_data = AnalyticsRepository.get_top_methods(
            limit=limit,
            from_date=from_date,
            to_date=to_date
        )

        # Transform to response model
        methods = [
            TopMethodAnalytics(
                method_id=row['method_id'],
                name=row['name'] or f"Method {row['method_id']}",
                calls=row['calls'],
                tokens_used=int(row.get('tokens_used', 0)),
                avg_tokens=int(row.get('avg_tokens', 0))
            )
            for row in raw_data
        ]

        response = TopMethodsResponse(
            success=True,
            methods=methods,
            total=len(methods)
        )

        return jsonify(response.model_dump()), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid parameter',
            'message': str(e)
        }), 400

    except Exception as e:
        current_app.logger.error(f"ERROR in admin_get_top_methods: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Failed to fetch top methods',
            'details': str(e)
        }), 500
