"""
LernsystemX Organisation Analytics - Top Reports Endpoints

Top reports endpoints:
- GET /api/v1/organisations/<org_id>/analytics/top-courses
- GET /api/v1/organisations/<org_id>/analytics/top-modules

Phase B10 - ISO 27001:2013 compliant
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Optional, Tuple

from app.models.analytics import (
    OrgTopCoursesResponse,
    OrgTopCourseAnalytics,
    OrgTopModulesResponse,
    OrgTopModuleAnalytics
)
from app.repositories.analytics import AnalyticsRepository
from app.middleware.auth import token_required, get_current_user
from app.security.permissions import require_permission, Permissions
from .time_series import check_org_access, parse_date_range


# Blueprint for top reports
reports_bp = Blueprint(
    'org_analytics_reports',
    __name__
)


@reports_bp.route('/organisations/<int:org_id>/analytics/top-courses', methods=['GET'])
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
            organization_id=org_id,
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


@reports_bp.route('/organisations/<int:org_id>/analytics/top-modules', methods=['GET'])
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
            organization_id=org_id,
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
