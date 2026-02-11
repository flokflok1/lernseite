"""
Admin Groups API - Group-Based Authorization (GBA) Management

Admin endpoints for managing authorization groups, members, and permissions.
Replaces legacy RBAC with flexible group-based authorization.

Endpoints:
- GET /admin/groups - List all groups
- POST /admin/groups - Create new group
- GET /admin/groups/<id> - Get group details
- PUT /admin/groups/<id> - Update group
- DELETE /admin/groups/<id> - Delete group
- GET /admin/groups/<id>/members - List group members
- POST /admin/groups/<id>/members - Add member to group
- DELETE /admin/groups/<id>/members/<user_id> - Remove member
- GET /admin/groups/<id>/permissions - List group permissions
- POST /admin/groups/<id>/permissions - Grant permission to group
- DELETE /admin/groups/<id>/permissions/<perm_id> - Revoke permission

ISO 27001:2013 compliant - Admin-only endpoints
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from flask import Blueprint, jsonify, request, g
from typing import Dict, Any, Tuple, List, Optional
import logging

from app.setup.group_setup import GroupSetup
from app.api.middleware.auth import token_required, admin_required
from app.infrastructure.utils.exceptions import NotFoundError, ValidationError
from app.infrastructure.persistence.database.connection import execute_query, fetch_one, fetch_all

logger = logging.getLogger(__name__)

# Blueprint
bp = Blueprint(
    'admin_groups',
    __name__,
    url_prefix='/admin/groups'
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _get_group_by_id(group_id: str) -> Optional[Dict]:
    """Get a single group by ID."""
    result = fetch_one(
        """
        SELECT id, name, slug, description, hierarchy_level, group_type,
               organisation_id, is_system_group, is_protected, created_at, updated_at
        FROM core.groups
        WHERE id = %s
        """,
        (group_id,)
    )
    if result:
        return {
            'id': result['id'],
            'name': result['name'],
            'slug': result['slug'],
            'description': result['description'],
            'hierarchy_level': result['hierarchy_level'],
            'group_type': result['group_type'],
            'organisation_id': result['organisation_id'],
            'is_system_group': result['is_system_group'],
            'is_protected': result['is_protected'],
            'created_at': result['created_at'].isoformat() if result['created_at'] else None,
            'updated_at': result['updated_at'].isoformat() if result['updated_at'] else None
        }
    return None


def _get_group_members(
    group_id: str,
    limit: int = 50,
    offset: int = 0
) -> Tuple[List[Dict], int]:
    """Get members of a group with pagination."""
    # Get members
    members = fetch_all(
        """
        SELECT ug.user_id, ug.access_level, ug.joined_at, ug.is_active,
               u.email, u.full_name, u.username
        FROM core.users_groups ug
        JOIN core.users u ON ug.user_id = u.user_id
        WHERE ug.group_id = %s AND ug.is_active = TRUE
        ORDER BY ug.joined_at DESC
        LIMIT %s OFFSET %s
        """,
        (group_id, limit, offset)
    )

    # Get total count
    count_result = fetch_one(
        """
        SELECT COUNT(*) as total
        FROM core.users_groups
        WHERE group_id = %s AND is_active = TRUE
        """,
        (group_id,)
    )
    total = count_result['total'] if count_result else 0

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


def _update_group(group_id: str, data: Dict) -> Optional[Dict]:
    """Update a group."""
    # Build update query dynamically
    allowed_fields = ['name', 'description', 'hierarchy_level', 'group_type']
    updates = []
    params = []

    for field in allowed_fields:
        if field in data:
            updates.append(f"{field} = %s")
            params.append(data[field])

    if not updates:
        return _get_group_by_id(group_id)

    params.append(group_id)

    result = execute_query(
        f"""
        UPDATE core.groups
        SET {', '.join(updates)}, updated_at = NOW()
        WHERE id = %s AND is_protected = FALSE
        RETURNING id, name, slug, description, hierarchy_level, group_type,
                  is_system_group, is_protected, created_at, updated_at
        """,
        tuple(params),
        fetch_one=True
    )

    if result:
        return {
            'id': result['id'],
            'name': result['name'],
            'slug': result['slug'],
            'description': result['description'],
            'hierarchy_level': result['hierarchy_level'],
            'group_type': result['group_type'],
            'is_system_group': result['is_system_group'],
            'is_protected': result['is_protected'],
            'created_at': result['created_at'].isoformat() if result['created_at'] else None,
            'updated_at': result['updated_at'].isoformat() if result['updated_at'] else None
        }
    return None


def _delete_group(group_id: str) -> bool:
    """Delete a group (only if not protected)."""
    result = execute_query(
        """
        DELETE FROM core.groups
        WHERE id = %s AND is_protected = FALSE
        RETURNING id
        """,
        (group_id,),
        fetch_one=True
    )
    return result is not None


def _remove_member(group_id: str, user_id: str) -> bool:
    """Remove a member from a group."""
    result = execute_query(
        """
        UPDATE core.users_groups
        SET is_active = FALSE, left_at = NOW()
        WHERE group_id = %s AND user_id = %s
        RETURNING user_id
        """,
        (group_id, user_id),
        fetch_one=True
    )
    return result is not None


def _revoke_permission(group_id: str, permission_id: str) -> bool:
    """Revoke a permission from a group."""
    result = execute_query(
        """
        DELETE FROM core.group_permissions
        WHERE group_id = %s AND permission_id = %s
        RETURNING permission_id
        """,
        (group_id, permission_id),
        fetch_one=True
    )
    return result is not None


def _get_group_permissions_paginated(
    group_id: str,
    limit: int = 50,
    offset: int = 0
) -> Tuple[List[Dict], int]:
    """Get permissions of a group with pagination."""
    permissions = fetch_all(
        """
        SELECT p.id, p.code, p.display_name, p.category, p.description, gp.created_at
        FROM core.group_permissions gp
        JOIN core.permissions p ON gp.permission_id = p.id
        WHERE gp.group_id = %s
        ORDER BY p.code ASC
        LIMIT %s OFFSET %s
        """,
        (group_id, limit, offset)
    )

    count_result = fetch_one(
        """
        SELECT COUNT(*) as total
        FROM core.group_permissions
        WHERE group_id = %s
        """,
        (group_id,)
    )
    total = count_result['total'] if count_result else 0

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


# ============================================================================
# GROUP CRUD ENDPOINTS
# ============================================================================

@bp.route('', methods=['GET'])
@token_required
@admin_required
def list_groups() -> Tuple[Dict[str, Any], int]:
    """
    GET /admin/groups

    List all groups with pagination.

    Query Parameters:
        - limit: Max results (default: 20, max: 100)
        - offset: Skip N results (default: 0)
        - organisation_id: Optional org filter

    Returns:
        200: {data: Group[], total: int}
    """
    try:
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = int(request.args.get('offset', 0))
        organisation_id = request.args.get('organisation_id')

        groups = GroupSetup.get_all_groups(organisation_id=organisation_id)

        # Apply pagination
        total = len(groups)
        paginated = groups[offset:offset + limit]

        return jsonify({
            'data': paginated,
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        logger.exception(f"Error listing groups: {e}")
        return jsonify({
            'error': {
                'code': 'GROUPS_LIST_ERROR',
                'message': 'Failed to list groups'
            }
        }), 500


# ============================================================================
# PERMISSIONS REGISTRY (ALL PERMISSIONS)
# IMPORTANT: Must be defined BEFORE /<group_id> routes to avoid shadowing
# ============================================================================

@bp.route('/permissions/registry', methods=['GET'])
@token_required
@admin_required
def list_all_permissions() -> Tuple[Dict[str, Any], int]:
    """
    GET /admin/groups/permissions/registry

    List ALL available permissions from the registry, grouped by category.
    Used by the PermissionsOverview to display assignable permissions.

    Query Parameters:
        - category: Optional category filter

    Returns:
        200: {data: Permission[], total: int, categories: str[]}
    """
    try:
        category = request.args.get('category')

        if category:
            permissions = fetch_all(
                """
                SELECT id, code, display_name, category, description
                FROM core.permissions
                WHERE category = %s
                ORDER BY category, code ASC
                """,
                (category,)
            )
        else:
            permissions = fetch_all(
                """
                SELECT id, code, display_name, category, description
                FROM core.permissions
                ORDER BY category, code ASC
                """
            )

        # Get distinct categories
        categories_result = fetch_all(
            """
            SELECT DISTINCT category
            FROM core.permissions
            ORDER BY category ASC
            """
        )
        categories = [c['category'] for c in categories_result] if categories_result else []

        data = [
            {
                'id': p['id'],
                'code': p['code'],
                'display_name': p['display_name'],
                'category': p['category'],
                'description': p['description']
            }
            for p in permissions
        ]

        return jsonify({
            'data': data,
            'total': len(data),
            'categories': categories
        }), 200

    except Exception as e:
        logger.exception(f"Error listing permissions registry: {e}")
        return jsonify({
            'error': {
                'code': 'PERMISSIONS_REGISTRY_ERROR',
                'message': 'Failed to list permissions registry'
            }
        }), 500


# ============================================================================
# SINGLE GROUP ENDPOINTS
# ============================================================================

@bp.route('/<group_id>', methods=['GET'])
@token_required
@admin_required
def get_group(group_id: str) -> Tuple[Dict[str, Any], int]:
    """
    GET /admin/groups/<group_id>

    Get single group by ID.

    Returns:
        200: {data: Group}
        404: Group not found
    """
    try:
        group = _get_group_by_id(group_id)

        if not group:
            return jsonify({
                'error': {
                    'code': 'GROUP_NOT_FOUND',
                    'message': f'Group {group_id} not found'
                }
            }), 404

        return jsonify({'data': group}), 200

    except Exception as e:
        logger.exception(f"Error getting group {group_id}: {e}")
        return jsonify({
            'error': {
                'code': 'GROUP_GET_ERROR',
                'message': 'Failed to get group'
            }
        }), 500


@bp.route('', methods=['POST'])
@token_required
@admin_required
def create_group() -> Tuple[Dict[str, Any], int]:
    """
    POST /admin/groups

    Create new group.

    Request Body:
        - name: Group name (required)
        - slug: URL-safe identifier (required)
        - description: Group description (optional)
        - hierarchy_level: Auth level 1-1000 (required)
        - type: Group type (optional, default: 'custom')

    Returns:
        201: {data: Group}
        400: Validation error
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Request body required'
                }
            }), 400

        # Validate required fields
        required = ['name', 'slug']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({
                'error': {
                    'code': 'MISSING_FIELDS',
                    'message': f"Missing required fields: {', '.join(missing)}"
                }
            }), 400

        # Default hierarchy level if not provided
        hierarchy_level = data.get('hierarchy_level', 100)

        group = GroupSetup.create_group(
            name=data['name'],
            slug=data['slug'],
            description=data.get('description', ''),
            hierarchy_level=hierarchy_level,
            group_type=data.get('type', 'custom'),
            organisation_id=data.get('organisation_id'),
            is_system_group=False,
            is_protected=False
        )

        return jsonify({'data': group}), 201

    except ValueError as e:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        logger.exception(f"Error creating group: {e}")
        return jsonify({
            'error': {
                'code': 'GROUP_CREATE_ERROR',
                'message': 'Failed to create group'
            }
        }), 500


@bp.route('/<group_id>', methods=['PUT', 'PATCH'])
@token_required
@admin_required
def update_group(group_id: str) -> Tuple[Dict[str, Any], int]:
    """
    PUT/PATCH /admin/groups/<group_id>

    Update group.

    Request Body (partial):
        - name: Group name
        - description: Group description
        - hierarchy_level: Auth level 1-1000
        - type: Group type

    Returns:
        200: {data: Group}
        400: Validation error
        404: Group not found
    """
    try:
        # Check if group exists
        existing = _get_group_by_id(group_id)
        if not existing:
            return jsonify({
                'error': {
                    'code': 'GROUP_NOT_FOUND',
                    'message': f'Group {group_id} not found'
                }
            }), 404

        # Check if protected
        if existing.get('is_protected'):
            return jsonify({
                'error': {
                    'code': 'GROUP_PROTECTED',
                    'message': 'Cannot modify protected system group'
                }
            }), 403

        data = request.get_json() or {}

        # Map 'type' to 'group_type'
        if 'type' in data:
            data['group_type'] = data.pop('type')

        group = _update_group(group_id, data)

        if not group:
            return jsonify({
                'error': {
                    'code': 'GROUP_UPDATE_FAILED',
                    'message': 'Failed to update group'
                }
            }), 400

        return jsonify({'data': group}), 200

    except Exception as e:
        logger.exception(f"Error updating group {group_id}: {e}")
        return jsonify({
            'error': {
                'code': 'GROUP_UPDATE_ERROR',
                'message': 'Failed to update group'
            }
        }), 500


@bp.route('/<group_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_group(group_id: str) -> Tuple[Dict[str, Any], int]:
    """
    DELETE /admin/groups/<group_id>

    Delete group (only if not protected).

    Returns:
        204: No content
        403: Cannot delete protected group
        404: Group not found
    """
    try:
        existing = _get_group_by_id(group_id)
        if not existing:
            return jsonify({
                'error': {
                    'code': 'GROUP_NOT_FOUND',
                    'message': f'Group {group_id} not found'
                }
            }), 404

        if existing.get('is_protected') or existing.get('is_system_group'):
            return jsonify({
                'error': {
                    'code': 'GROUP_PROTECTED',
                    'message': 'Cannot delete protected or system group'
                }
            }), 403

        if not _delete_group(group_id):
            return jsonify({
                'error': {
                    'code': 'GROUP_DELETE_FAILED',
                    'message': 'Failed to delete group'
                }
            }), 400

        return '', 204

    except Exception as e:
        logger.exception(f"Error deleting group {group_id}: {e}")
        return jsonify({
            'error': {
                'code': 'GROUP_DELETE_ERROR',
                'message': 'Failed to delete group'
            }
        }), 500


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


__all__ = ['bp']
