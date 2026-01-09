"""
LernsystemX Admin System Dashboard API

System-wide dashboard analytics for administrators.

Endpoints:
    - GET /api/v1/dashboard/admin/system/overview - System overview stats
    - GET /api/v1/dashboard/admin/system/activity - Recent activity
    - GET /api/v1/dashboard/admin/system/users - User statistics
    - GET /api/v1/dashboard/admin/system/courses - Course statistics
    - GET /api/v1/dashboard/admin/system/ai-usage - AI usage statistics

Permissions: Admin only
ISO 27001:2013 compliant - Admin analytics
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta

from app.middleware.auth import token_required, role_required
from app.repositories.dashboard.core import DashboardRepository as AdminDashboardRepository


admin_dashboard_bp = Blueprint(
    'admin_dashboard',
    __name__,
    url_prefix='/dashboard/admin/system'
)


@admin_dashboard_bp.route('/overview', methods=['GET'])
@token_required
@role_required('admin')
def get_system_overview():
    """
    Get system overview statistics.

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: System overview stats

    Example Response:
        {
            "success": true,
            "overview": {
                "total_users": 15234,
                "active_users_today": 892,
                "total_courses": 456,
                "published_courses": 289,
                "total_enrollments": 45678,
                "ai_requests_today": 1234,
                "system_health": "healthy",
                "uptime_days": 87
            }
        }
    """
    try:
        overview = AdminDashboardRepository.get_system_overview()

        return jsonify({
            'success': True,
            'overview': overview
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get system overview',
            'details': str(e)
        }), 500


@admin_dashboard_bp.route('/activity', methods=['GET'])
@token_required
@role_required('admin')
def get_recent_activity():
    """
    Get recent system activity.

    Headers:
        Authorization: Bearer <access_token>

    Query Parameters:
        limit: Max activities (default: 50)
        hours: Time window in hours (default: 24)

    Response:
        200: Recent activity list

    Example Response:
        {
            "success": true,
            "activities": [
                {
                    "timestamp": "2026-01-08T10:30:00Z",
                    "type": "course_published",
                    "user_id": "uuid",
                    "user_email": "creator@example.com",
                    "resource_type": "course",
                    "resource_id": "uuid",
                    "details": "Published course 'Python Basics'"
                }
            ],
            "count": 45
        }
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        hours = request.args.get('hours', 24, type=int)

        # Calculate time window
        since = datetime.utcnow() - timedelta(hours=hours)

        activities = AdminDashboardRepository.get_recent_activity(
            since=since,
            limit=limit
        )

        return jsonify({
            'success': True,
            'activities': activities,
            'count': len(activities)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get recent activity',
            'details': str(e)
        }), 500


@admin_dashboard_bp.route('/users', methods=['GET'])
@token_required
@role_required('admin')
def get_user_statistics():
    """
    Get user statistics.

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: User statistics

    Example Response:
        {
            "success": true,
            "stats": {
                "total_users": 15234,
                "by_role": {
                    "user": 12000,
                    "premium": 2500,
                    "creator": 500,
                    "teacher": 150,
                    "admin": 10
                },
                "new_users_7d": 234,
                "new_users_30d": 1024,
                "active_users_7d": 5678,
                "active_users_30d": 12000,
                "churn_rate_30d": 0.05
            }
        }
    """
    try:
        stats = AdminDashboardRepository.get_user_statistics()

        return jsonify({
            'success': True,
            'stats': stats
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get user statistics',
            'details': str(e)
        }), 500


@admin_dashboard_bp.route('/courses', methods=['GET'])
@token_required
@role_required('admin')
def get_course_statistics():
    """
    Get course statistics.

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Course statistics

    Example Response:
        {
            "success": true,
            "stats": {
                "total_courses": 456,
                "published_courses": 289,
                "draft_courses": 167,
                "courses_by_category": {
                    "IT & Software": 120,
                    "Business": 80,
                    "Languages": 60
                },
                "total_enrollments": 45678,
                "avg_enrollments_per_course": 158,
                "most_popular_courses": [
                    {
                        "course_id": "uuid",
                        "title": "Python Basics",
                        "enrollments": 2345
                    }
                ]
            }
        }
    """
    try:
        stats = AdminDashboardRepository.get_course_statistics()

        return jsonify({
            'success': True,
            'stats': stats
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get course statistics',
            'details': str(e)
        }), 500


@admin_dashboard_bp.route('/ai-usage', methods=['GET'])
@token_required
@role_required('admin')
def get_ai_usage_statistics():
    """
    Get AI usage statistics.

    Headers:
        Authorization: Bearer <access_token>

    Query Parameters:
        days: Time window in days (default: 7)

    Response:
        200: AI usage statistics

    Example Response:
        {
            "success": true,
            "stats": {
                "total_requests": 12345,
                "requests_by_type": {
                    "content_generation": 5000,
                    "recommendations": 3000,
                    "translation": 2000,
                    "tutor": 2345
                },
                "requests_by_provider": {
                    "anthropic": 7000,
                    "openai": 5345
                },
                "total_tokens_used": 5678900,
                "total_cost_usd": 234.56,
                "avg_response_time_ms": 1234
            }
        }
    """
    try:
        days = request.args.get('days', 7, type=int)

        # Calculate time window
        since = datetime.utcnow() - timedelta(days=days)

        stats = AdminDashboardRepository.get_ai_usage_statistics(
            since=since
        )

        return jsonify({
            'success': True,
            'stats': stats
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get AI usage statistics',
            'details': str(e)
        }), 500
