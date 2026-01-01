"""
LernsystemX Organisation Analytics API

Advanced analytics endpoints for organisation administrators:
- GET /api/v1/organisations/<org_id>/analytics/events/time-series
- GET /api/v1/organisations/<org_id>/analytics/active-members/time-series
- GET /api/v1/organisations/<org_id>/analytics/top-courses
- GET /api/v1/organisations/<org_id>/analytics/top-modules

Phase B10 - ISO 27001:2013 compliant
"""

from flask import request, jsonify
from datetime import datetime, timedelta

from app.api import api_v1
from app.models.analytics import (
    TimeSeriesResponse,
    TimeSeriesDataPoint,
    OrgTopCoursesResponse,
    OrgTopCourseAnalytics,
    OrgTopModulesResponse,
    OrgTopModuleAnalytics
)
from app.repositories.analytics_repository import AnalyticsRepository
from app.middleware.auth import token_required, get_current_user
from app.security.permissions import require_permission, Permissions


def parse_date_range(range_param: str):
    """Parse range parameter to from_date and to_date"""
    range_map = {
        '7d': 7,
        '30d': 30,
        '90d': 90
    }

    days = range_map.get(range_param, 7)
    to_date = datetime.utcnow()
    from_date = to_date - timedelta(days=days)

    return from_date, to_date


def check_org_access(user, org_id: int):
    """
    Check if user has access to organisation analytics

    Args:
        user: Current user
        org_id: Organisation ID

    Raises:
        PermissionError: If user doesn't have access
    """
    # System admin and superadmin can access all orgs
    if user.get('role') in ['admin', 'superadmin']:
        return

    # Org members can only access their own org
    user_org_id = user.get('organisation_id')
    if user_org_id != org_id:
        raise PermissionError(f"Access denied to organisation {org_id}")


@api_v1.route('/organisations/<int:org_id>/analytics/events/time-series', methods=['GET'])
@token_required
@require_permission(Permissions.VIEW_ORG_ANALYTICS)
def org_get_events_time_series(org_id: int):
    """
    Get organisation events time series

    Path Parameters:
        org_id: Organisation ID

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
        403: Forbidden (user not in organisation)
        500: Server error

    Security:
        Requires: VIEW_ORG_ANALYTICS permission
        Multi-tenancy: User must belong to organisation
    """
    try:
        user = get_current_user()

        # Check org access (multi-tenancy)
        check_org_access(user, org_id)

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
            from_date,
            to_date,
            organisation_id=org_id
        )

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

    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': str(e)
        }), 403

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


@api_v1.route('/organisations/<int:org_id>/analytics/active-members/time-series', methods=['GET'])
@token_required
@require_permission(Permissions.VIEW_ORG_ANALYTICS)
def org_get_active_members_time_series(org_id: int):
    """
    Get organisation active members time series

    Path Parameters:
        org_id: Organisation ID

    Query Parameters:
        range: Time range - '7d', '30d', '90d' (default: 7d)
        from: Start date (YYYY-MM-DD)
        to: End date (YYYY-MM-DD)

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

        401: Unauthorized
        403: Forbidden
        500: Server error

    Security:
        Requires: VIEW_ORG_ANALYTICS permission
        Multi-tenancy: User must belong to organisation
    """
    try:
        user = get_current_user()

        # Check org access
        check_org_access(user, org_id)

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
            from_date,
            to_date,
            organisation_id=org_id
        )

        # Transform to response model
        data_points = [
            TimeSeriesDataPoint(
                date=str(row['date']),
                value=row['count']
            )
            for row in raw_data
        ]

        # Total unique members (max of daily counts)
        total = max((point.value for point in data_points), default=0)

        response = TimeSeriesResponse(
            success=True,
            data=data_points,
            total=total
        )

        return jsonify(response.model_dump()), 200

    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': str(e)
        }), 403

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid date format',
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch active members time series',
            'details': str(e)
        }), 500


@api_v1.route('/organisations/<int:org_id>/analytics/top-courses', methods=['GET'])
@token_required
@require_permission(Permissions.VIEW_ORG_ANALYTICS)
def org_get_top_courses(org_id: int):
    """
    Get top courses for organisation

    Path Parameters:
        org_id: Organisation ID

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
                    "title": "Python Basics",
                    "enrolled_count": 25,
                    "avg_progress": 68.5,
                    "completion_rate": 44.0,
                    "events_count": 320
                }
            ],
            "total": 10
        }

        401: Unauthorized
        403: Forbidden
        500: Server error

    Security:
        Requires: VIEW_ORG_ANALYTICS permission
        Multi-tenancy: User must belong to organisation
    """
    try:
        user = get_current_user()

        # Check org access
        check_org_access(user, org_id)

        # Parse query parameters
        limit = min(int(request.args.get('limit', 10)), 100)
        range_param = request.args.get('range')
        from_str = request.args.get('from')
        to_str = request.args.get('to')

        # Determine date range
        from_date, to_date = None, None
        if from_str and to_str:
            from_date = datetime.strptime(from_str, '%Y-%m-%d')
            to_date = datetime.strptime(to_str, '%Y-%m-%d')
        elif range_param:
            from_date, to_date = parse_date_range(range_param)

        # Fetch top courses from repository
        raw_data = AnalyticsRepository.get_org_top_courses(
            organisation_id=org_id,
            limit=limit,
            from_date=from_date,
            to_date=to_date
        )

        # Transform to response model
        courses = [
            OrgTopCourseAnalytics(
                course_id=row['course_id'],
                title=row['title'] or f"Course {row['course_id']}",
                enrolled_count=row['enrolled_count'],
                avg_progress=float(row.get('avg_progress', 0)),
                completion_rate=float(row.get('completion_rate', 0)) if row.get('completion_rate') else None,
                events_count=row.get('events_count')
            )
            for row in raw_data
        ]

        response = OrgTopCoursesResponse(
            success=True,
            courses=courses,
            total=len(courses)
        )

        return jsonify(response.model_dump()), 200

    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': str(e)
        }), 403

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid parameter',
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch top courses',
            'details': str(e)
        }), 500


@api_v1.route('/organisations/<int:org_id>/analytics/top-modules', methods=['GET'])
@token_required
@require_permission(Permissions.VIEW_ORG_ANALYTICS)
def org_get_top_modules(org_id: int):
    """
    Get top modules for organisation

    Path Parameters:
        org_id: Organisation ID

    Query Parameters:
        limit: Number of top modules (default: 10, max: 100)
        range: Time range - '7d', '30d', '90d'
        from: Start date (YYYY-MM-DD)
        to: End date (YYYY-MM-DD)

    Response:
        200: Top modules data
        {
            "success": true,
            "modules": [
                {
                    "module_id": 15,
                    "module_title": "Variables & Data Types",
                    "course_title": "Python Basics",
                    "completions": 18,
                    "avg_time_spent": 45
                }
            ],
            "total": 10
        }

        401: Unauthorized
        403: Forbidden
        500: Server error

    Security:
        Requires: VIEW_ORG_ANALYTICS permission
        Multi-tenancy: User must belong to organisation
    """
    try:
        user = get_current_user()

        # Check org access
        check_org_access(user, org_id)

        # Parse query parameters
        limit = min(int(request.args.get('limit', 10)), 100)
        range_param = request.args.get('range')
        from_str = request.args.get('from')
        to_str = request.args.get('to')

        # Determine date range
        from_date, to_date = None, None
        if from_str and to_str:
            from_date = datetime.strptime(from_str, '%Y-%m-%d')
            to_date = datetime.strptime(to_str, '%Y-%m-%d')
        elif range_param:
            from_date, to_date = parse_date_range(range_param)

        # Fetch top modules from repository
        raw_data = AnalyticsRepository.get_org_top_modules(
            organisation_id=org_id,
            limit=limit,
            from_date=from_date,
            to_date=to_date
        )

        # Transform to response model
        modules = [
            OrgTopModuleAnalytics(
                module_id=row['module_id'],
                module_title=row['module_title'] or f"Module {row['module_id']}",
                course_title=row['course_title'] or "Unknown Course",
                completions=row['completions'],
                avg_time_spent=int(row.get('avg_time_spent', 0)) if row.get('avg_time_spent') else None
            )
            for row in raw_data
        ]

        response = OrgTopModulesResponse(
            success=True,
            modules=modules,
            total=len(modules)
        )

        return jsonify(response.model_dump()), 200

    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': str(e)
        }), 403

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid parameter',
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch top modules',
            'details': str(e)
        }), 500
