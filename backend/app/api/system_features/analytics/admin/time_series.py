"""
Analytics Time Series Endpoints (DDD)

Admin endpoints for system-wide time series analytics.
Uses AnalyticsQueryFactory and AnalyticsAggregationService.
"""

from flask import request, jsonify, g
from typing import Dict, Any, Tuple
import logging

from app.extensions import limiter
from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.repositories.analytics.analytics import AnalyticsRepository
from app.models.analytics import TimeSeriesResponse

from app.api.system_features.analytics.core import (
    AnalyticsQueryFactory,
    AnalyticsAggregationService,
    TimeRange
)

from . import analytics_time_series_bp

logger = logging.getLogger(__name__)


@analytics_time_series_bp.route('/events/time-series', methods=['GET'])
@token_required
@require_permission(Permissions.VIEW_SYSTEM_ANALYTICS)
@limiter.limit("60 per minute")
def get_events_time_series() -> Tuple[Dict[str, Any], int]:
    """
    Get system-wide events time series.

    Query Parameters:
        range (str): Time range - '7d', '30d', '90d' (default: 7d)
        from (str): Start date (YYYY-MM-DD) - overrides range
        to (str): End date (YYYY-MM-DD) - overrides range

    Returns:
        JSON response with time series data

    Security:
        Requires: VIEW_SYSTEM_ANALYTICS permission (admin, superadmin)

    DDD: Uses AnalyticsQueryFactory, AnalyticsAggregationService
    """
    try:
        # Parse query parameters
        range_param = request.args.get('range', '7d')
        from_str = request.args.get('from')
        to_str = request.args.get('to')

        # DDD: Use Factory to create query configuration
        query_config = AnalyticsQueryFactory.create_time_series_query(
            time_range=None,  # Will be determined from params
            from_str=from_str,
            to_str=to_str
        )

        # If no explicit dates, use range parameter
        if not (from_str and to_str):
            time_range = TimeRange.from_string(range_param)
            query_config = AnalyticsQueryFactory.create_time_series_query(
                time_range=time_range
            )

        # Fetch time series from repository
        raw_data = AnalyticsRepository.get_events_time_series(
            from_date=query_config['from_date'],
            to_date=query_config['to_date']
        )

        # DDD: Use Service to aggregate data
        data_points, total = AnalyticsAggregationService.aggregate_time_series(
            raw_data=raw_data,
            date_key='date',
            value_key='count'
        )

        # Build response using Pydantic model
        response = TimeSeriesResponse(
            success=True,
            data=[point.to_dict() for point in data_points],
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


@analytics_time_series_bp.route('/active-users/time-series', methods=['GET'])
@token_required
@require_permission(Permissions.VIEW_SYSTEM_ANALYTICS)
@limiter.limit("60 per minute")
def get_active_users_time_series() -> Tuple[Dict[str, Any], int]:
    """
    Get system-wide active users time series.

    Query Parameters:
        range (str): Time range - '7d', '30d', '90d' (default: 7d)
        from (str): Start date (YYYY-MM-DD)
        to (str): End date (YYYY-MM-DD)

    Returns:
        JSON response with time series data

    Security:
        Requires: VIEW_SYSTEM_ANALYTICS permission

    DDD: Uses AnalyticsQueryFactory, AnalyticsAggregationService
    """
    try:
        # Parse query parameters
        range_param = request.args.get('range', '7d')
        from_str = request.args.get('from')
        to_str = request.args.get('to')

        # DDD: Use Factory to create query configuration
        query_config = AnalyticsQueryFactory.create_time_series_query(
            from_str=from_str,
            to_str=to_str
        )

        # If no explicit dates, use range parameter
        if not (from_str and to_str):
            time_range = TimeRange.from_string(range_param)
            query_config = AnalyticsQueryFactory.create_time_series_query(
                time_range=time_range
            )

        # Fetch time series from repository
        raw_data = AnalyticsRepository.get_active_users_time_series(
            from_date=query_config['from_date'],
            to_date=query_config['to_date']
        )

        # DDD: Use Service to aggregate data
        data_points, _ = AnalyticsAggregationService.aggregate_time_series(
            raw_data=raw_data,
            date_key='date',
            value_key='count'
        )

        # DDD: Calculate total unique users (max daily count)
        total = AnalyticsAggregationService.calculate_total_unique_users(data_points)

        # Build response using Pydantic model
        response = TimeSeriesResponse(
            success=True,
            data=[point.to_dict() for point in data_points],
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
