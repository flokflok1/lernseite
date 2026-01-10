"""
Organisations Domain - Time Series Routes (Analytics Journey)

Time series analytics endpoints:
- GET /organisations/<org_id>/analytics/events/time-series
- GET /organisations/<org_id>/analytics/active-members/time-series

Architecture: Journey-Based DDD
Database: PostgreSQL via AnalyticsRepository (direct SQL)
ISO 27001:2013 compliant - Organisation analytics
"""

from flask import Blueprint

from ._helpers import (
    request, jsonify,
    datetime,
    TimeSeriesResponse, TimeSeriesDataPoint,
    AnalyticsRepository,
    token_required, get_current_user,
    require_permission, Permissions,
    parse_date_range, check_org_access
)


time_series_bp = Blueprint(
    'org_analytics_time_series',
    __name__
)


@time_series_bp.route('/organisations/<int:org_id>/analytics/events/time-series', methods=['GET'])
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


@time_series_bp.route('/organisations/<int:org_id>/analytics/active-members/time-series', methods=['GET'])
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
