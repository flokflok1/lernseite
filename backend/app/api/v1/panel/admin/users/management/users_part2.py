"""
LernsystemX Admin API - User Management (Part 2: Moderation Actions)

Admin endpoints for user moderation: ban, unban, delete, and creator verification.

Endpoints:
- POST /api/v1/admin/users/{id}/ban - Ban user
- POST /api/v1/admin/users/{id}/unban - Unban user
- DELETE /api/v1/admin/users/{id} - Delete user (soft or hard)
- POST /api/v1/admin/users/{id}/verify - Verify creator status

See users.py for CRUD and group management endpoints.

Phase B24 - Admin User Management Implementation
"""

from flask import jsonify, request, g

from app.api.v1 import api_v1
from app.api.middleware.auth import permission_required
from app.infrastructure.persistence.repositories.user.admin_part2 import UserAdminModerationRepository
from app.application.services.system.audit.service import AuditService


# ==========================================
# MODERATION ENDPOINTS
# ==========================================

@api_v1.route('/admin/users/<string:user_id>/ban', methods=['POST'])
@permission_required('admin.users:write')
def admin_ban_user(user_id: str):
    """
    Ban user with reason and optional duration.

    Path Parameters:
        user_id (str): User ID

    Request Body:
        {
            "reason": "Violation of terms",  // Required
            "duration_days": 7               // Optional (null = permanent)
        }

    Response:
        200: User banned successfully
        400: Missing reason
        403: Forbidden (insufficient permissions)
        404: User not found
        500: Server error
    """
    try:
        data = request.get_json()
        reason = data.get('reason')
        duration_days = data.get('duration_days')

        if not reason:
            return jsonify({
                'success': False,
                'error': 'Missing required field',
                'message': 'reason is required'
            }), 400

        success = UserAdminModerationRepository.admin_ban_user(
            user_id=user_id,
            reason=reason,
            banned_by_user_id=g.current_user['user_id'],
            duration_days=duration_days
        )

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to ban user',
                'message': 'User not found or already banned'
            }), 404

        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='ban_user',
            resource_type='admin_users',
            resource_id=user_id,
            severity='high',
            details={'reason': reason, 'duration_days': duration_days}
        )

        return jsonify({
            'success': True,
            'message': 'User banned successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to ban user',
            'message': str(e)
        }), 500


@api_v1.route('/admin/users/<string:user_id>/unban', methods=['POST'])
@permission_required('admin.users:write')
def admin_unban_user(user_id: str):
    """
    Unban user.

    Path Parameters:
        user_id (str): User ID

    Response:
        200: User unbanned successfully
        403: Forbidden (insufficient permissions)
        404: User not found or not banned
        500: Server error
    """
    try:
        success = UserAdminModerationRepository.admin_unban_user(
            user_id=user_id,
            unbanned_by_user_id=g.current_user['user_id']
        )

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to unban user',
                'message': 'User not found or not currently banned'
            }), 404

        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='unban_user',
            resource_type='admin_users',
            resource_id=user_id,
            severity='medium'
        )

        return jsonify({
            'success': True,
            'message': 'User unbanned successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to unban user',
            'message': str(e)
        }), 500


@api_v1.route('/admin/users/<string:user_id>', methods=['DELETE'])
@permission_required('admin.users:delete')
def admin_delete_user(user_id: str):
    """
    Delete user (soft or hard delete).

    Path Parameters:
        user_id (str): User ID

    Query Parameters:
        hard (bool): If true, permanently delete (default: false = soft delete)

    Response:
        200: User deleted successfully
        403: Forbidden (insufficient permissions)
        404: User not found
        500: Server error
    """
    try:
        hard_delete = request.args.get('hard', 'false').lower() == 'true'

        success = UserAdminModerationRepository.admin_delete_user(
            user_id=user_id,
            deleted_by_user_id=g.current_user['user_id'],
            hard_delete=hard_delete
        )

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to delete user',
                'message': 'User not found'
            }), 404

        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='delete_user',
            resource_type='admin_users',
            resource_id=user_id,
            severity='critical',
            details={'hard_delete': hard_delete}
        )

        delete_type = "permanently deleted" if hard_delete else "soft deleted"
        return jsonify({
            'success': True,
            'message': f'User {delete_type} successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to delete user',
            'message': str(e)
        }), 500


@api_v1.route('/admin/users/<string:user_id>/verify', methods=['POST'])
@permission_required('admin.users:write')
def admin_verify_creator(user_id: str):
    """
    Verify creator status for user.

    Path Parameters:
        user_id (str): User ID

    Response:
        200: Creator verified successfully
        403: Forbidden (insufficient permissions)
        404: User not found or not a creator
        500: Server error
    """
    try:
        success = UserAdminModerationRepository.admin_verify_creator(
            user_id=user_id,
            verified_by_user_id=g.current_user['user_id']
        )

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to verify creator',
                'message': 'User not found or not a creator'
            }), 404

        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='verify_creator',
            resource_type='admin_users',
            resource_id=user_id,
            severity='medium'
        )

        return jsonify({
            'success': True,
            'message': 'Creator verified successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to verify creator',
            'message': str(e)
        }), 500


__all__ = [
    'admin_ban_user',
    'admin_unban_user',
    'admin_delete_user',
    'admin_verify_creator',
]
