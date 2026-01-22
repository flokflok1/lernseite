"""
LernsystemX Admin System API - System Statistics Module

Endpoints:
- GET /api/v1/admin/stats/users - User statistics
- GET /api/v1/admin/stats/courses - Course statistics
- GET /api/v1/admin/stats/system - System statistics

Phase 2.1 - Admin Dashboard Implementation
"""

from flask import jsonify, current_app, g
from datetime import datetime

from .system_operations import api_v1
from app.infrastructure.security.permissions import require_permission, Permissions
from app.infrastructure.persistence.repositories.admin.core import AdminRepository
from app.domain.models.admin import UserStatsResponse, CourseStatsResponse, SystemStatsResponse
from app.application.services.audit_service import AuditService


@api_v1.route('/admin/stats/users', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_admin_dashboard_user_stats():
    """
    Get user statistics for admin dashboard.

    Returns metrics about total, active, banned, and new users.

    **Endpoint:** GET /api/v1/admin/stats/users

    **Authentication:** Required (Admin only)

    **Permissions:** ADMIN_SYSTEM_READ

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "total_users": 1250,
            "active_users": 450,
            "banned_users": 12,
            "new_users_30d": 87
        }
    }
    ```

    **Status Codes:**
    - 200: Success
    - 401: Unauthorized
    - 403: Forbidden (not admin)
    - 500: Server error
    """
    try:
        # Get user statistics from repository
        stats = AdminRepository.get_user_stats()

        # Validate response with Pydantic model
        response_data = UserStatsResponse(**stats)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='view_stats',
            resource_type='admin_stats',
            severity='info',
            details={'stats_type': 'users'}
        )

        return jsonify({
            'success': True,
            'data': response_data.dict(),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get user stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve user statistics',
            'message': str(e)
        }), 500


@api_v1.route('/admin/stats/courses', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_admin_dashboard_course_stats():
    """
    Get course statistics for admin dashboard.

    Returns metrics about total, published, pending, and rejected courses.

    **Endpoint:** GET /api/v1/admin/stats/courses

    **Authentication:** Required (Admin only)

    **Permissions:** ADMIN_SYSTEM_READ

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "total_courses": 342,
            "published": 298,
            "pending_review": 32,
            "rejected": 12
        }
    }
    ```

    **Status Codes:**
    - 200: Success
    - 401: Unauthorized
    - 403: Forbidden (not admin)
    - 500: Server error
    """
    try:
        # Get course statistics from repository
        stats = AdminRepository.get_course_stats()

        # Validate response with Pydantic model
        response_data = CourseStatsResponse(**stats)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='view_stats',
            resource_type='admin_stats',
            severity='info',
            details={'stats_type': 'courses'}
        )

        return jsonify({
            'success': True,
            'data': response_data.dict(),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get course stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve course statistics',
            'message': str(e)
        }), 500


@api_v1.route('/admin/stats/system', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_admin_dashboard_system_stats():
    """
    Get system statistics for admin dashboard.

    Returns metrics about uptime, database latency, requests, and error rate.

    **Endpoint:** GET /api/v1/admin/stats/system

    **Authentication:** Required (Admin only)

    **Permissions:** ADMIN_SYSTEM_READ

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "uptime": 123456.78,
            "db_latency": 12.34,
            "request_count_24h": 45678,
            "error_rate": 0.12
        }
    }
    ```

    **Status Codes:**
    - 200: Success
    - 401: Unauthorized
    - 403: Forbidden (not admin)
    - 500: Server error
    """
    try:
        # Get application start time for uptime calculation
        app_start_time = current_app.config.get('APP_START_TIME', datetime.utcnow())

        # Get system statistics from repository
        stats = AdminRepository.get_system_stats(app_start_time)

        # Validate response with Pydantic model
        response_data = SystemStatsResponse(**stats)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='view_stats',
            resource_type='admin_stats',
            severity='info',
            details={'stats_type': 'system'}
        )

        return jsonify({
            'success': True,
            'data': response_data.dict(),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get system stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve system statistics',
            'message': str(e)
        }), 500
