"""
Admin Roles & Permissions API
=============================
API endpoints for managing roles, permissions, and user assignments.
"""

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import get_jwt_identity
from app.services.roles_service import RolesService
from app.middleware.auth import permission_required
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('admin_roles', __name__, url_prefix='/admin/roles')


# =============================================================================
# Roles CRUD
# =============================================================================

@bp.route('', methods=['GET'])
@permission_required('roles.view')
def get_roles():
    """
    Get all roles.

    Query params:
        include_system: bool (default: true) - Include system roles
    """
    include_system = request.args.get('include_system', 'true').lower() == 'true'
    roles = RolesService.get_all_roles(include_system=include_system)

    return jsonify({
        'success': True,
        'data': roles
    })


@bp.route('/<int:role_id>', methods=['GET'])
@permission_required('roles.view')
def get_role(role_id: int):
    """Get single role with permissions."""
    role = RolesService.get_role(role_id)

    if not role:
        return jsonify({
            'success': False,
            'error': {'code': 'NOT_FOUND', 'message': 'Role not found'}
        }), 404

    return jsonify({
        'success': True,
        'data': role
    })


@bp.route('', methods=['POST'])
@permission_required('roles.create')
def create_role():
    """
    Create a new custom role.

    Request body:
    {
        "role_name": "reviewer",
        "display_name": "Reviewer",
        "description": "Can review content",
        "hierarchy_level": 4,
        "color": "#3b82f6",
        "icon": "eye"
    }
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    required = ['role_name', 'display_name']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_INPUT', 'message': f'Missing fields: {", ".join(missing)}'}
        }), 400

    role_id = RolesService.create_role(
        role_name=data['role_name'],
        display_name=data['display_name'],
        description=data.get('description'),
        hierarchy_level=data.get('hierarchy_level', 1),
        color=data.get('color', '#6b7280'),
        icon=data.get('icon', 'user'),
        created_by=user_id
    )

    if not role_id:
        return jsonify({
            'success': False,
            'error': {'code': 'CREATE_FAILED', 'message': 'Failed to create role'}
        }), 500

    return jsonify({
        'success': True,
        'data': {'role_id': role_id}
    }), 201


@bp.route('/<int:role_id>', methods=['PUT'])
@permission_required('roles.edit')
def update_role(role_id: int):
    """
    Update a role.

    Note: System roles can only have color/icon updated.
    """
    data = request.get_json()

    # Check if role exists
    role = RolesService.get_role(role_id)
    if not role:
        return jsonify({
            'success': False,
            'error': {'code': 'NOT_FOUND', 'message': 'Role not found'}
        }), 404

    # System roles: only color and icon
    if role.get('is_system'):
        success = RolesService.update_role(
            role_id,
            color=data.get('color'),
            icon=data.get('icon')
        )
    else:
        success = RolesService.update_role(
            role_id,
            display_name=data.get('display_name'),
            description=data.get('description'),
            hierarchy_level=data.get('hierarchy_level'),
            color=data.get('color'),
            icon=data.get('icon')
        )

    return jsonify({'success': success})


@bp.route('/<int:role_id>', methods=['DELETE'])
@permission_required('roles.delete')
def delete_role(role_id: int):
    """Delete a custom role. Users will be moved to 'free' role."""
    role = RolesService.get_role(role_id)

    if not role:
        return jsonify({
            'success': False,
            'error': {'code': 'NOT_FOUND', 'message': 'Role not found'}
        }), 404

    if role.get('is_system'):
        return jsonify({
            'success': False,
            'error': {'code': 'FORBIDDEN', 'message': 'Cannot delete system roles'}
        }), 403

    success = RolesService.delete_role(role_id)
    return jsonify({'success': success})


# =============================================================================
# Permissions
# =============================================================================

@bp.route('/permissions', methods=['GET'])
@permission_required('roles.view')
def get_permissions():
    """
    Get all available permissions.

    Query params:
        category: string - Filter by category
        grouped: bool - Return grouped by category
    """
    category = request.args.get('category')
    grouped = request.args.get('grouped', 'false').lower() == 'true'

    if grouped:
        data = RolesService.get_permissions_grouped()
    else:
        data = RolesService.get_all_permissions(category=category)

    return jsonify({
        'success': True,
        'data': data
    })


# =============================================================================
# Role-Permission Assignments
# =============================================================================

@bp.route('/<int:role_id>/permissions', methods=['GET'])
@permission_required('roles.view')
def get_role_permissions(role_id: int):
    """Get all permissions for a role."""
    permissions = RolesService.get_role_permissions(role_id)

    return jsonify({
        'success': True,
        'data': permissions
    })


@bp.route('/<int:role_id>/permissions', methods=['PUT'])
@permission_required('roles.permissions.assign')
def set_role_permissions(role_id: int):
    """
    Set permissions for a role (replaces all existing).

    Request body:
    {
        "permission_ids": [1, 2, 3, 5]
    }
    """
    data = request.get_json()
    permission_ids = data.get('permission_ids', [])

    if not isinstance(permission_ids, list):
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_INPUT', 'message': 'permission_ids must be an array'}
        }), 400

    success = RolesService.set_role_permissions(role_id, permission_ids)
    return jsonify({'success': success})


@bp.route('/<int:role_id>/permissions/<int:permission_id>', methods=['POST'])
@permission_required('roles.permissions.assign')
def add_role_permission(role_id: int, permission_id: int):
    """Add single permission to role."""
    success = RolesService.add_role_permission(role_id, permission_id)
    return jsonify({'success': success})


@bp.route('/<int:role_id>/permissions/<int:permission_id>', methods=['DELETE'])
@permission_required('roles.permissions.assign')
def remove_role_permission(role_id: int, permission_id: int):
    """Remove single permission from role."""
    success = RolesService.remove_role_permission(role_id, permission_id)
    return jsonify({'success': success})


# =============================================================================
# Role Users
# =============================================================================

@bp.route('/<int:role_id>/users', methods=['GET'])
@permission_required('users.view')
def get_role_users(role_id: int):
    """Get users with a specific role."""
    limit = min(int(request.args.get('limit', 100)), 500)
    users = RolesService.get_users_by_role(role_id, limit=limit)

    return jsonify({
        'success': True,
        'data': users
    })


@bp.route('/<int:role_id>/users/<user_id>', methods=['PUT'])
@permission_required('users.roles.assign')
def assign_user_role(role_id: int, user_id: str):
    """Assign role to a user."""
    success = RolesService.assign_role_to_user(user_id, role_id)
    return jsonify({'success': success})


# =============================================================================
# User Permission Overrides
# =============================================================================

@bp.route('/users/<user_id>/permissions', methods=['GET'])
@permission_required('users.view')
def get_user_permissions(user_id: str):
    """
    Get user's effective permissions and overrides.

    Returns:
        effective: All permissions the user has (role + overrides)
        overrides: User-specific permission overrides
    """
    effective = RolesService.get_user_effective_permissions(user_id)
    overrides = RolesService.get_user_permission_overrides(user_id)

    return jsonify({
        'success': True,
        'data': {
            'effective': effective,
            'overrides': overrides
        }
    })


@bp.route('/users/<user_id>/permissions/<int:permission_id>', methods=['PUT'])
@permission_required('users.roles.assign')
def set_user_permission_override(user_id: str, permission_id: int):
    """
    Set user permission override.

    Request body:
    {
        "granted": true,
        "expires_at": "2025-12-31T23:59:59Z",  // optional
        "reason": "Temporary access for project"  // optional
    }
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    granted = data.get('granted', True)
    expires_at = data.get('expires_at')
    reason = data.get('reason')

    success = RolesService.set_user_permission_override(
        user_id=user_id,
        permission_id=permission_id,
        granted=granted,
        granted_by=current_user_id,
        expires_at=expires_at,
        reason=reason
    )

    return jsonify({'success': success})


@bp.route('/users/<user_id>/permissions/<int:permission_id>', methods=['DELETE'])
@permission_required('users.roles.assign')
def remove_user_permission_override(user_id: str, permission_id: int):
    """Remove user permission override."""
    success = RolesService.remove_user_permission_override(user_id, permission_id)
    return jsonify({'success': success})


@bp.route('/users/<user_id>/check/<permission_key>', methods=['GET'])
@permission_required('users.view')
def check_user_permission(user_id: str, permission_key: str):
    """Check if user has a specific permission."""
    has_permission = RolesService.check_user_permission(user_id, permission_key)

    return jsonify({
        'success': True,
        'data': {'has_permission': has_permission}
    })


# =============================================================================
# Register Blueprint
# =============================================================================

from app.api.v1.admin.system_operations import api_v1
api_v1.register_blueprint(bp)
