"""
Admin Group Management API - RBAC 3.0 Group Management Endpoints

Handles group CRUD, membership management, and permission assignments.

PHASE B: Complete group management REST API implementation.
"""

from flask import Blueprint, request, jsonify, g
from app.api.middleware.auth import token_required, require_admin
from app.application.services.system.group_management import GroupManagementService
from app.infrastructure.persistence.repositories.group import GroupRepository
import logging

logger = logging.getLogger(__name__)

groups_bp = Blueprint('admin_groups', __name__, url_prefix='/admin/groups')


# =====================================================
# Group CRUD Operations
# =====================================================

@groups_bp.route('', methods=['GET'])
@token_required
@require_admin
def list_groups():
    """
    List groups with pagination and filters

    Query Parameters:
        - page: Page number (default 1)
        - per_page: Items per page (default 50, max 100)
        - organisation_id: Filter by organisation
        - group_type: Filter by type (department, class, team, custom, etc.)
        - search: Search by name or slug
        - sort: Sort field (created_at, name)
        - order: Sort order (asc, desc)

    Returns:
        200: {success: true, groups: [...], pagination: {...}}
        400: Invalid query parameters
        401: Unauthorized
        403: Forbidden (not admin)
    """
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        organisation_id = request.args.get('organisation_id')
        group_type = request.args.get('group_type')
        search = request.args.get('search')
        sort = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc')

        # Validate pagination
        if page < 1 or per_page < 1:
            return jsonify({'error': 'Invalid pagination parameters'}), 400

        # Build filters
        offset = (page - 1) * per_page
        groups = GroupRepository.find_all(
            organisation_id=organisation_id,
            group_type=group_type,
            limit=per_page,
            offset=offset
        )

        # Apply search filter if specified
        if search:
            groups = [g for g in groups if search.lower() in g.get('name', '').lower() or search.lower() in g.get('slug', '').lower()]

        # Count total
        total = GroupRepository.count(organisation_id=organisation_id, group_type=group_type)

        # Convert UUIDs to strings
        for group in groups:
            if 'group_id' in group:
                group['group_id'] = str(group['group_id'])
            if 'organisation_id' in group and group['organisation_id']:
                group['organisation_id'] = str(group['organisation_id'])

        return jsonify({
            'data': groups,
            'total': total,
            'limit': per_page,
            'offset': offset
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error listing groups: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@groups_bp.route('/<group_id>', methods=['GET'])
@token_required
@require_admin
def get_group(group_id: str):
    """
    Get group details

    Path Parameters:
        - group_id: Group ID (UUID)

    Returns:
        200: {success: true, group: {...}}
        404: Group not found
        401: Unauthorized
        403: Forbidden (not admin)
    """
    try:
        group = GroupRepository.find_by_id(group_id)

        if not group:
            return jsonify({'error': 'Group not found'}), 404

        # Convert UUIDs
        if 'group_id' in group:
            group['group_id'] = str(group['group_id'])
        if 'organisation_id' in group and group['organisation_id']:
            group['organisation_id'] = str(group['organisation_id'])

        # Get members count
        members_data = GroupRepository.get_members(group_id, limit=0)
        group['member_count'] = members_data['total']

        # Get permissions
        group['permissions'] = GroupManagementService.get_group_permissions(group_id)

        return jsonify({'data': group}), 200

    except Exception as e:
        logger.error(f"Error getting group: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@groups_bp.route('', methods=['POST'])
@token_required
@require_admin
def create_group():
    """
    Create new group

    Request Body:
        - name: Group name (required, 2-100 chars)
        - slug: URL-safe identifier (required, 3-50 chars, alphanumeric/dash/underscore)
        - organisation_id: Organisation ID (optional, null for system groups)
        - group_type: Group type (optional, default: custom)
        - description: Description (optional)
        - parent_group_id: Parent group ID for hierarchy (optional)

    Returns:
        201: {success: true, group: {...}}
        400: Validation error
        401: Unauthorized
        403: Forbidden (not admin)
        409: Conflict (slug already exists)
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('name') or not data.get('slug'):
            return jsonify({'error': 'name and slug are required'}), 400

        # Create group
        group = GroupManagementService.create_group(
            name=data['name'],
            slug=data['slug'],
            organisation_id=data.get('organisation_id'),
            group_type=data.get('group_type', 'custom'),
            description=data.get('description'),
            parent_group_id=data.get('parent_group_id'),
            created_by=g.current_user['user_id']
        )

        # Convert UUIDs
        if 'group_id' in group:
            group['group_id'] = str(group['group_id'])
        if 'organisation_id' in group and group['organisation_id']:
            group['organisation_id'] = str(group['organisation_id'])

        return jsonify({'data': group}), 201

    except ValueError as e:
        status = 409 if 'already exists' in str(e) else 400
        return jsonify({'error': str(e)}), status
    except Exception as e:
        logger.error(f"Error creating group: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@groups_bp.route('/<group_id>', methods=['PUT'])
@token_required
@require_admin
def update_group(group_id: str):
    """
    Update group

    Path Parameters:
        - group_id: Group ID (UUID)

    Request Body:
        - name: New name (optional)
        - description: New description (optional)
        - metadata: JSON metadata (optional)

    Returns:
        200: {success: true, group: {...}}
        400: Validation error
        404: Group not found
        401: Unauthorized
        403: Forbidden (not admin or system group)
    """
    try:
        data = request.get_json() or {}

        # Update group
        group = GroupManagementService.update_group(
            group_id=group_id,
            updates=data,
            updated_by=g.current_user['user_id']
        )

        if not group:
            return jsonify({'error': 'Group not found'}), 404

        # Convert UUIDs
        if 'group_id' in group:
            group['group_id'] = str(group['group_id'])
        if 'organisation_id' in group and group['organisation_id']:
            group['organisation_id'] = str(group['organisation_id'])

        return jsonify({'data': group}), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400 if 'not found' not in str(e) else 404
    except Exception as e:
        logger.error(f"Error updating group: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@groups_bp.route('/<group_id>', methods=['DELETE'])
@token_required
@require_admin
def delete_group(group_id: str):
    """
    Delete group (with protections for system/protected groups)

    Path Parameters:
        - group_id: Group ID (UUID)

    Returns:
        204: No Content (success)
        400: Cannot delete (has members, system group, etc.)
        404: Group not found
        401: Unauthorized
        403: Forbidden (not admin)
    """
    try:
        result = GroupManagementService.delete_group(
            group_id=group_id,
            deleted_by=g.current_user['user_id']
        )

        if not result:
            return jsonify({'error': 'Group not found'}), 404

        return '', 204

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error deleting group: {e}")
        return jsonify({'error': 'Internal server error'}), 500


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
