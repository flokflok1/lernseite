"""
Admin Groups API - Members & Permissions Endpoints (Part 2)

Continuation of routes.py for group member and permission management.

Endpoints:
- GET /admin/groups/<id>/members - List group members
- POST /admin/groups/<id>/members - Add member to group
- DELETE /admin/groups/<id>/members/<user_id> - Remove member
- GET /admin/groups/<id>/permissions - List group permissions
- POST /admin/groups/<id>/permissions - Grant permission to group
- DELETE /admin/groups/<id>/permissions/<perm_id> - Revoke permission

ISO 27001:2013 compliant - Admin-only endpoints
"""

from flask import jsonify, request, g
from typing import Dict, Any, Tuple, List
import logging

from app.setup.initialization.groups import GroupSetup
from app.api.middleware.auth import token_required, admin_required
from app.infrastructure.persistence.repositories.group.admin_queries import GroupAdminQueryRepository
from app.api.v1.panel.admin.groups.routes import bp, _get_group_by_id

logger = logging.getLogger(__name__)


# ============================================================================
# HELPER FUNCTIONS (Members & Permissions)
# ============================================================================

def _get_group_members(
    group_id: str,
    limit: int = 50,
    offset: int = 0
) -> Tuple[List[Dict], int]:
    """Get members of a group with pagination."""
    members = GroupAdminQueryRepository.get_group_members(group_id, limit, offset)
    total = GroupAdminQueryRepository.count_group_members(group_id)

    return [
        {
            'user_id': m['user_id'],
            'email': m['email'],
            'full_name': m['full_name'],
            'username': m['username'],
            'access_level': m['access_level'],
            'joined_at': m['joined_at'].isoformat() if m['joined_at'] else None,
            'is_active': m['is_active']
        }
        for m in members
    ], total


def _remove_member(group_id: str, user_id: str) -> bool:
    """Remove a member from a group."""
    return GroupAdminQueryRepository.remove_member(group_id, user_id)


def _get_group_permissions_paginated(
    group_id: str,
    limit: int = 50,
    offset: int = 0
) -> Tuple[List[Dict], int]:
    """Get permissions of a group with pagination."""
    permissions = GroupAdminQueryRepository.get_group_permissions_paginated(group_id, limit, offset)
    total = GroupAdminQueryRepository.count_group_permissions(group_id)

    return [
        {
            'id': p['id'],
            'code': p['code'],
            'display_name': p['display_name'],
            'category': p['category'],
            'description': p['description'],
            'assigned_at': p['created_at'].isoformat() if p['created_at'] else None
        }
        for p in permissions
    ], total


def _revoke_permission(group_id: str, permission_id: str) -> bool:
    """Revoke a permission from a group."""
    return GroupAdminQueryRepository.revoke_permission(group_id, permission_id)


# ============================================================================
# MEMBERS ENDPOINTS
# ============================================================================

@bp.route('/<group_id>/members', methods=['GET'])
@token_required
@admin_required
def list_group_members(group_id: str) -> Tuple[Dict[str, Any], int]:
    """
    GET /admin/groups/<group_id>/members

    List group members with pagination.

    Returns:
        200: {data: Member[], total: int}
        404: Group not found
    """
    try:
        # Check if group exists
        if not _get_group_by_id(group_id):
            return jsonify({
                'error': {
                    'code': 'GROUP_NOT_FOUND',
                    'message': f'Group {group_id} not found'
                }
            }), 404

        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))

        members, total = _get_group_members(group_id, limit, offset)

        return jsonify({
            'data': members,
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        logger.exception(f"Error listing members for group {group_id}: {e}")
        return jsonify({
            'error': {
                'code': 'MEMBERS_LIST_ERROR',
                'message': 'Failed to list group members'
            }
        }), 500


@bp.route('/<group_id>/members', methods=['POST'])
@token_required
@admin_required
def add_group_member(group_id: str) -> Tuple[Dict[str, Any], int]:
    """
    POST /admin/groups/<group_id>/members

    Add member to group.

    Request Body:
        - user_id: User ID (required)
        - access_level: Access level (optional, default: 'member')

    Returns:
        201: {data: Member}
        400: Validation error
        404: Group not found
    """
    try:
        # Check if group exists
        if not _get_group_by_id(group_id):
            return jsonify({
                'error': {
                    'code': 'GROUP_NOT_FOUND',
                    'message': f'Group {group_id} not found'
                }
            }), 404

        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({
                'error': {
                    'code': 'MISSING_USER_ID',
                    'message': 'user_id is required'
                }
            }), 400

        # Get admin user ID from token
        admin_user_id = getattr(g, 'user_id', None)

        assignment = GroupSetup.assign_group_to_user(
            user_id=data['user_id'],
            group_id=group_id,
            admin_user_id=admin_user_id,
            access_level=data.get('access_level', 'member')
        )

        return jsonify({'data': assignment}), 201

    except ValueError as e:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        logger.exception(f"Error adding member to group {group_id}: {e}")
        return jsonify({
            'error': {
                'code': 'MEMBER_ADD_ERROR',
                'message': 'Failed to add member to group'
            }
        }), 500


@bp.route('/<group_id>/members/<user_id>', methods=['DELETE'])
@token_required
@admin_required
def remove_group_member(group_id: str, user_id: str) -> Tuple[Dict[str, Any], int]:
    """
    DELETE /admin/groups/<group_id>/members/<user_id>

    Remove member from group.

    Returns:
        204: No content
        404: Group or member not found
    """
    try:
        if not _get_group_by_id(group_id):
            return jsonify({
                'error': {
                    'code': 'GROUP_NOT_FOUND',
                    'message': f'Group {group_id} not found'
                }
            }), 404

        if not _remove_member(group_id, user_id):
            return jsonify({
                'error': {
                    'code': 'MEMBER_NOT_FOUND',
                    'message': f'User {user_id} is not a member of this group'
                }
            }), 404

        return '', 204

    except Exception as e:
        logger.exception(f"Error removing member {user_id} from group {group_id}: {e}")
        return jsonify({
            'error': {
                'code': 'MEMBER_REMOVE_ERROR',
                'message': 'Failed to remove member from group'
            }
        }), 500


# ============================================================================
# PERMISSIONS ENDPOINTS
# ============================================================================

@bp.route('/<group_id>/permissions', methods=['GET'])
@token_required
@admin_required
def list_group_permissions(group_id: str) -> Tuple[Dict[str, Any], int]:
    """
    GET /admin/groups/<group_id>/permissions

    List group permissions with pagination.

    Returns:
        200: {data: Permission[], total: int}
        404: Group not found
    """
    try:
        if not _get_group_by_id(group_id):
            return jsonify({
                'error': {
                    'code': 'GROUP_NOT_FOUND',
                    'message': f'Group {group_id} not found'
                }
            }), 404

        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))

        permissions, total = _get_group_permissions_paginated(group_id, limit, offset)

        return jsonify({
            'data': permissions,
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        logger.exception(f"Error listing permissions for group {group_id}: {e}")
        return jsonify({
            'error': {
                'code': 'PERMISSIONS_LIST_ERROR',
                'message': 'Failed to list group permissions'
            }
        }), 500


@bp.route('/<group_id>/permissions', methods=['POST'])
@token_required
@admin_required
def grant_group_permission(group_id: str) -> Tuple[Dict[str, Any], int]:
    """
    POST /admin/groups/<group_id>/permissions

    Grant permission to group.

    Request Body:
        - permission: Permission code (required)

    Returns:
        201: {data: Permission}
        400: Validation error
        404: Group not found
    """
    try:
        if not _get_group_by_id(group_id):
            return jsonify({
                'error': {
                    'code': 'GROUP_NOT_FOUND',
                    'message': f'Group {group_id} not found'
                }
            }), 404

        data = request.get_json()
        if not data or 'permission' not in data:
            return jsonify({
                'error': {
                    'code': 'MISSING_PERMISSION',
                    'message': 'permission is required'
                }
            }), 400

        admin_user_id = getattr(g, 'user_id', None)

        result = GroupSetup.assign_permission_to_group(
            group_id=group_id,
            permission_code=data['permission'],
            admin_user_id=admin_user_id
        )

        return jsonify({'data': result}), 201

    except ValueError as e:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        logger.exception(f"Error granting permission to group {group_id}: {e}")
        return jsonify({
            'error': {
                'code': 'PERMISSION_GRANT_ERROR',
                'message': 'Failed to grant permission to group'
            }
        }), 500


@bp.route('/<group_id>/permissions/<permission_id>', methods=['DELETE'])
@token_required
@admin_required
def revoke_group_permission(group_id: str, permission_id: str) -> Tuple[Dict[str, Any], int]:
    """
    DELETE /admin/groups/<group_id>/permissions/<permission_id>

    Revoke permission from group.

    Returns:
        204: No content
        404: Group or permission not found
    """
    try:
        if not _get_group_by_id(group_id):
            return jsonify({
                'error': {
                    'code': 'GROUP_NOT_FOUND',
                    'message': f'Group {group_id} not found'
                }
            }), 404

        if not _revoke_permission(group_id, permission_id):
            return jsonify({
                'error': {
                    'code': 'PERMISSION_NOT_FOUND',
                    'message': 'Permission not assigned to this group'
                }
            }), 404

        return '', 204

    except Exception as e:
        logger.exception(f"Error revoking permission {permission_id} from group {group_id}: {e}")
        return jsonify({
            'error': {
                'code': 'PERMISSION_REVOKE_ERROR',
                'message': 'Failed to revoke permission from group'
            }
        }), 500
