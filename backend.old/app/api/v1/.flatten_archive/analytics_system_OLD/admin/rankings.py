"""
Analytics Rankings Endpoints (DDD)

Admin endpoints for top courses and top learning methods analytics.
Uses AnalyticsQueryFactory and AnalyticsAggregationService.
"""

from flask import request, jsonify, g
from typing import Dict, Any, Tuple
import logging

from app.extensions import limiter
from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.repositories.analytics.analytics import AnalyticsRepository
from app.models.analytics import (
    TopCoursesResponse,
    TopCourseAnalytics,
    TopMethodsResponse,
    TopMethodAnalytics
)

from app.api.system_features.analytics.core import (
    AnalyticsQueryFactory,
    AnalyticsAggregationService,
    TimeRange
)

from . import analytics_rankings_bp

logger = logging.getLogger(__name__)


@analytics_rankings_bp.route('/top-courses', methods=['GET'])
@token_required
@require_permission(Permissions.VIEW_SYSTEM_ANALYTICS)
@limiter.limit("60 per minute")
def get_top_courses() -> Tuple[Dict[str, Any], int]:
    """
    Get top courses by activity.

    Query Parameters:
        limit (int): Number of top courses (default: 10, max: 100)
        range (str): Time range - '7d', '30d', '90d'
        from (str): Start date (YYYY-MM-DD)
        to (str): End date (YYYY-MM-DD)

    Returns:
        JSON response with top courses data

    Security:
        Requires: VIEW_SYSTEM_ANALYTICS permission

    DDD: Uses AnalyticsQueryFactory, AnalyticsAggregationService
    """
    try:
        # Parse query parameters
        limit = int(request.args.get('limit', 10))
        range_param = request.args.get('range')
        days_param = request.args.get('days')  # Legacy parameter
        from_str = request.args.get('from')
        to_str = request.args.get('to')

        # DDD: Use Factory to create query configuration
        query_config = AnalyticsQueryFactory.create_ranking_query(
            limit=limit,
            from_str=from_str,
            to_str=to_str
        )

        # Handle range parameter if no explicit dates
        if not (from_str and to_str) and (range_param or days_param):
            # Convert days_param to range_param format if needed
            if days_param and not range_param:
                range_param = f"{days_param}d"

            time_range = TimeRange.from_string(range_param)
            query_config = AnalyticsQueryFactory.create_ranking_query(
                limit=limit,
                time_range=time_range
            )

        # Fetch top courses from repository
        raw_data = AnalyticsRepository.get_top_courses(
            limit=query_config['limit'],
            from_date=query_config['from_date'],
            to_date=query_config['to_date']
        )

        # Transform to response model
        courses = []
        for row in raw_data:
            # DDD: Use Service to calculate completion rate
            completion_rate = AnalyticsAggregationService.calculate_completion_rate(
                completions=row['completions'],
                enrollments=row['enrollments']
            )

            courses.append(
                TopCourseAnalytics(
                    course_id=row['course_id'],
                    title=row['title'] or f"Course {row['course_id']}",
                    events_count=row['events_count'],
                    enrollments=row['enrollments'],
                    completions=row['completions'],
                    avg_completion_rate=completion_rate
                )
            )

        # Build response using Pydantic model
        response = TopCoursesResponse(
            success=True,
            courses=courses,
            total=len(courses)
        )

        return jsonify(response.model_dump()), 200

    except ValueError as ve:
        logger.warning(f"Invalid parameters for top courses: {ve}")
        return jsonify({
            'success': False,
            'error': 'Invalid parameter',
            'message': str(ve)
        }), 400

    except Exception as e:
        logger.error(f"Error fetching top courses: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch top courses',
            'details': str(e)
        }), 500


@analytics_rankings_bp.route('/top-methods', methods=['GET'])
@token_required
@require_permission(Permissions.VIEW_SYSTEM_ANALYTICS)
@limiter.limit("60 per minute")
def get_top_methods() -> Tuple[Dict[str, Any], int]:
    """
    Get top learning methods by usage.

    Query Parameters:
        limit (int): Number of top methods (default: 10, max: 100)
        range (str): Time range - '7d', '30d', '90d'
        from (str): Start date (YYYY-MM-DD)
        to (str): End date (YYYY-MM-DD)

    Returns:
        JSON response with top methods data

    Security:
        Requires: VIEW_SYSTEM_ANALYTICS permission

    DDD: Uses AnalyticsQueryFactory, AnalyticsAggregationService
    """
    try:
        # Parse query parameters
        limit = int(request.args.get('limit', 10))
        range_param = request.args.get('range')
        days_param = request.args.get('days')  # Legacy parameter
        from_str = request.args.get('from')
        to_str = request.args.get('to')

        # DDD: Use Factory to create query configuration
        query_config = AnalyticsQueryFactory.create_ranking_query(
            limit=limit,
            from_str=from_str,
            to_str=to_str
        )

        # Handle range parameter if no explicit dates
        if not (from_str and to_str) and (range_param or days_param):
            # Convert days_param to range_param format if needed
            if days_param and not range_param:
                range_param = f"{days_param}d"

            time_range = TimeRange.from_string(range_param)
            query_config = AnalyticsQueryFactory.create_ranking_query(
                limit=limit,
                time_range=time_range
            )

        # Fetch top methods from repository
        raw_data = AnalyticsRepository.get_top_methods(
            limit=query_config['limit'],
            from_date=query_config['from_date'],
            to_date=query_config['to_date']
        )

        # Transform to response model
        methods = []
        for row in raw_data:
            # DDD: Use Service to calculate average tokens
            avg_tokens = AnalyticsAggregationService.calculate_average_tokens(
                total_tokens=int(row.get('tokens_used', 0)),
                calls=row['calls']
            )

            methods.append(
                TopMethodAnalytics(
                    method_id=row['method_id'],
                    name=row['name'] or f"Method {row['method_id']}",
                    calls=row['calls'],
                    tokens_used=int(row.get('tokens_used', 0)),
                    avg_tokens=avg_tokens
                )
            )

        # Build response using Pydantic model
        response = TopMethodsResponse(
            success=True,
            methods=methods,
            total=len(methods)
        )

        return jsonify(response.model_dump()), 200

    except ValueError as ve:
        logger.warning(f"Invalid parameters for top methods: {ve}")
        return jsonify({
            'success': False,
            'error': 'Invalid parameter',
            'message': str(ve)
        }), 400

    except Exception as e:
        logger.error(f"Error fetching top methods: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch top methods',
            'details': str(e)
        }), 500
