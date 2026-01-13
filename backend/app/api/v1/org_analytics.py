"""
LernsystemX Organisation Analytics API - Consolidated

Organisation-specific analytics and reporting.

Organisation Statistics:
- GET /organisations/:id/stats - Get organisation statistics

Organisation Reports:
- GET /organisations/:id/analytics/top-courses - Top courses for organisation
- GET /organisations/:id/analytics/top-modules - Top modules for organisation

Organisation Time Series:
- GET /organisations/:id/analytics/events/time-series - Organisation events time series
- GET /organisations/:id/analytics/active-members/time-series - Active members time series

All routes: /api/v1/organisations/*
ISO 27001:2013 compliant - Organisation Analytics Layer
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from typing import Tuple, Optional, List

from app.middleware.auth import token_required, get_current_user
from app.security.permissions import require_permission, Permissions
from app.models.analytics import (
    TimeSeriesResponse,
    TimeSeriesDataPoint,
    OrgTopCoursesResponse,
    OrgTopCourseAnalytics,
    OrgTopModulesResponse,
    OrgTopModuleAnalytics
)
from app.models.organisation import OrganisationStatsResponse
from app.repositories.analytics import AnalyticsRepository
from app.repositories.organisations.core import OrganisationRepository
from app.repositories.subscription import SubscriptionRepository
# Blueprint
org_analytics_bp = Blueprint('org_analytics', __name__, url_prefix='/organisations')

__all__ = ['org_analytics_bp']


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


def check_org_membership(user: dict, org_id: int, required_roles: Optional[List[str]] = None) -> bool:
    """
    Check if user is a member of organisation with optional role check.

    Args:
        user: Current user dictionary
        org_id: Organisation ID
        required_roles: Optional list of required org roles (e.g., ['org_admin', 'teacher'])

    Returns:
        True if user is member (and has required role if specified)
    """
    # Admins always have access (RBAC 2.0: dynamic from DB)
    from app.services.permission_service import PermissionService
    if PermissionService.check_threshold(user, 'analytics.view_all'):
        return True

    # Check basic membership
    if user.get('organization_id') != org_id:
        return False

    # If no specific role required, membership is enough
    if not required_roles:
        return True

    # Check org role
    from app.database.connection import fetch_one
    org_user_query = """
        SELECT org_role FROM organisation_users
        WHERE org_id = %s AND user_id = %s AND status = 'active'
    """
    org_user = fetch_one(org_user_query, (org_id, user['user_id']))

    if org_user and org_user['org_role'] in required_roles:
        return True

    return False


def check_org_access(user: dict, org_id: int) -> None:
    """
    Check if user has access to organisation analytics.

    Args:
        user: Current user
        org_id: Organisation ID

    Raises:
        PermissionError: If user doesn't have access
    """
    # System admin+ can access all orgs (RBAC 2.0: dynamic from DB)
    from app.services.permission_service import PermissionService
    if PermissionService.check_threshold(user, 'analytics.view_all'):
        return

    # Org members can only access their own org
    user_org_id = user.get('organization_id')
    if user_org_id != org_id:
        raise PermissionError(f"Access denied to organisation {org_id}")


# =============================================================================
# ORGANISATION STATISTICS
# =============================================================================

@org_analytics_bp.route('/<int:org_id>/stats', methods=['GET'])
@token_required
def get_organisation_stats(org_id: int):
    """
    Get organisation statistics.

    Path Parameters:
        org_id: Organisation ID

    Response:
        200: Organisation statistics
        - User counts (total, active, by role)
        - Course counts (total, active)
        - Class counts (for schools)
        - Token usage
        - Subscription info
        403: Insufficient permissions (org_admin or admin required)
        404: Organisation not found

    Permissions:
        - Admins can view stats of all organisations
        - org_admin can view stats of their organisation
    """
    try:
        current_user = get_current_user()

        # Check permissions - only org_admin can view stats
        if not check_org_membership(current_user, org_id, required_roles=['org_admin']):
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'Only organisation administrators can view statistics'
            }), 403

        # Check if organisation exists
        org = OrganisationRepository.get_organisation_by_id(org_id)
        if not org:
            return jsonify({
                'success': False,
                'error': 'Not Found',
                'message': f'Organisation with ID {org_id} not found'
            }), 404

        # Get base stats from repository
        stats = OrganisationRepository.get_organisation_stats(org_id)

        # Get subscription info (integration with SubscriptionRepository)
        try:
            subscription = SubscriptionRepository.get_subscription_for_organisation(org_id)
            if subscription:
                stats['subscription_plan'] = subscription.get('plan_name')
                stats['subscription_status'] = subscription.get('status')
                stats['subscription_expires_at'] = subscription.get('expires_at')
        except Exception:
            # Subscription repository may not be available yet
            pass

        # Convert to response model
        stats_response = OrganisationStatsResponse(**stats)

        return jsonify({
            'success': True,
            'stats': stats_response.model_dump()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get organisation statistics',
            'details': str(e)
        }), 500


# =============================================================================
# ORGANISATION TOP REPORTS
# =============================================================================

@org_analytics_bp.route('/<int:org_id>/analytics/top-courses', methods=['GET'])
@token_required
@require_permission(Permissions.VIEW_ORG_ANALYTICS)
def org_get_top_courses(org_id: int):
    """
    Get top courses for organisation.

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


@org_analytics_bp.route('/<int:org_id>/analytics/top-modules', methods=['GET'])
@token_required
@require_permission(Permissions.VIEW_ORG_ANALYTICS)
def org_get_top_modules(org_id: int):
    """
    Get top modules for organisation.

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


# =============================================================================
# ORGANISATION TIME SERIES
# =============================================================================

@org_analytics_bp.route('/<int:org_id>/analytics/events/time-series', methods=['GET'])
@token_required
@require_permission(Permissions.VIEW_ORG_ANALYTICS)
def org_get_events_time_series(org_id: int):
    """
    Get organisation events time series.

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
            organization_id=org_id
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


@org_analytics_bp.route('/<int:org_id>/analytics/active-members/time-series', methods=['GET'])
@token_required
@require_permission(Permissions.VIEW_ORG_ANALYTICS)
def org_get_active_members_time_series(org_id: int):
    """
    Get organisation active members time series.

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
            organization_id=org_id
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
