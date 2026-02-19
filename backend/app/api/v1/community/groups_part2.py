"""
Admin Group Management API - Membership & Permission Endpoints

Continuation of groups.py: handles membership management and
permission assignments for groups.

PHASE B: Complete group management REST API implementation.
"""

from flask import request, jsonify, g
from app.api.middleware.auth import token_required, require_admin
from app.application.services.system.group_management import GroupManagementService
from app.infrastructure.persistence.repositories.group import GroupRepository
from app.api.v1.community.groups import groups_bp
import logging

logger = logging.getLogger(__name__)


# =====================================================
# Membership Management
# =====================================================

@groups_bp.route('/<group_id>/members', methods=['GET'])
@token_required
@require_admin
def get_group_members(group_id: str):
    """
    Get group members with pagination

    Path Parameters:
        - group_id: Group ID (UUID)

    Query Parameters:
        - page: Page number (default 1)
        - per_page: Items per page (default 50, max 100)

    Returns:
        200: {success: true, members: [...], pagination: {...}}
        404: Group not found
        401: Unauthorized
        403: Forbidden (not admin)
    """
    try:
        if not GroupRepository.exists(group_id):
            return jsonify({'error': 'Group not found'}), 404

        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        offset = (page - 1) * per_page

        result = GroupManagementService.get_group_members(group_id, per_page, offset)

        return jsonify({
            'data': result['members'],
            'total': result['total'],
            'limit': per_page,
            'offset': offset
        }), 200

    except Exception as e:
        logger.error(f"Error getting group members: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@groups_bp.route('/<group_id>/members', methods=['POST'])
@token_required
@require_admin
def add_group_members(group_id: str):
    """
    Add user(s) to group

    Path Parameters:
        - group_id: Group ID (UUID)

    Request Body:
        - user_id: Single user ID (optional)
        - user_ids: List of user IDs (optional, for batch add)

    Returns:
        200: {success: true, message: '...', result: {...}}
        400: Invalid request
        404: Group not found
        401: Unauthorized
        403: Forbidden (not admin)
    """
    try:
        data = request.get_json() or {}

        if not GroupRepository.exists(group_id):
            return jsonify({'error': 'Group not found'}), 404

        # Handle batch add
        if 'user_ids' in data:
            result = GroupManagementService.batch_add_users(
                group_id=group_id,
                user_ids=data['user_ids'],
                added_by=g.current_user['user_id']
            )

            return jsonify({
                'data': result
            }), 200

        # Handle single add
        elif 'user_id' in data:
            result = GroupManagementService.add_user_to_group(
                group_id=group_id,
                user_id=data['user_id'],
                added_by=g.current_user['user_id']
            )

            return jsonify({
                'data': {'success': result}
            }), 200 if result else 400

        else:
            return jsonify({'error': 'user_id or user_ids required'}), 400

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error adding group members: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@groups_bp.route('/<group_id>/members/<user_id>', methods=['DELETE'])
@token_required
@require_admin
def remove_group_member(group_id: str, user_id: str):
    """
    Remove user from group

    Path Parameters:
        - group_id: Group ID (UUID)
        - user_id: User ID (UUID)

    Returns:
        204: No Content (success)
        404: Group or user not found
        401: Unauthorized
        403: Forbidden (not admin)
    """
    try:
        result = GroupManagementService.remove_user_from_group(
            group_id=group_id,
            user_id=user_id,
            removed_by=g.current_user['user_id']
        )

        return '', 204 if result else 404

    except Exception as e:
        logger.error(f"Error removing group member: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# =====================================================
# Permission Management
# =====================================================

@groups_bp.route('/<group_id>/permissions', methods=['GET'])
@token_required
@require_admin
def get_group_permissions(group_id: str):
    """
    Get group permissions

    Path Parameters:
        - group_id: Group ID (UUID)

    Returns:
        200: {success: true, permissions: [...]}
        404: Group not found
        401: Unauthorized
        403: Forbidden (not admin)
    """
    try:
        if not GroupRepository.exists(group_id):
            return jsonify({'error': 'Group not found'}), 404

        permissions = GroupManagementService.get_group_permissions(group_id)

        return jsonify({
            'data': permissions
        }), 200

    except Exception as e:
        logger.error(f"Error getting group permissions: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@groups_bp.route('/<group_id>/permissions', methods=['POST'])
@token_required
@require_admin
def assign_group_permissions(group_id: str):
    """
    Assign permission(s) to group

    Path Parameters:
        - group_id: Group ID (UUID)

    Request Body:
        - permission_key: Single permission (optional)
        - permission_keys: List of permissions (optional)

    Returns:
        200: {success: true, message: '...', result: {...}}
        400: Invalid request
        404: Group not found
        401: Unauthorized
        403: Forbidden (not admin)
    """
    try:
        data = request.get_json() or {}

        if not GroupRepository.exists(group_id):
            return jsonify({'error': 'Group not found'}), 404

        # Handle batch assign
        if 'permission_keys' in data:
            from app.infrastructure.persistence.repositories.group import GroupManagementRepository
            result = GroupManagementRepository.batch_assign_permissions(
                group_id=group_id,
                permission_keys=data['permission_keys'],
                assigned_by=g.current_user['user_id']
            )

            return jsonify({
                'data': result
            }), 200

        # Handle single assign
        elif 'permission_key' in data:
            result = GroupManagementService.assign_permission(
                group_id=group_id,
                permission_key=data['permission_key'],
                assigned_by=g.current_user['user_id']
            )

            return jsonify({
                'data': {'success': result}
            }), 200 if result else 400

        else:
            return jsonify({'error': 'permission_key or permission_keys required'}), 400

    except Exception as e:
        logger.error(f"Error assigning group permissions: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@groups_bp.route('/<group_id>/permissions/<permission_key>', methods=['DELETE'])
@token_required
@require_admin
def revoke_group_permission(group_id: str, permission_key: str):
    """
    Revoke permission from group

    Path Parameters:
        - group_id: Group ID (UUID)
        - permission_key: Permission key

    Returns:
        204: No Content (success)
        404: Group not found
        401: Unauthorized
        403: Forbidden (not admin)
    """
    try:
        result = GroupManagementService.revoke_permission(
            group_id=group_id,
            permission_key=permission_key,
            revoked_by=g.current_user['user_id']
        )

        return '', 204 if result else 404

    except Exception as e:
        logger.error(f"Error revoking permission: {e}")
        return jsonify({'error': 'Internal server error'}), 500
