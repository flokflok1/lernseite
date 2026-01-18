"""
RBAC 2.0 - Roles CRUD Operations

Endpoints for creating, reading, updating, and deleting roles.

Phase 5.3 - Owner-Admin & Dynamic Roles System
"""

from flask import Blueprint, jsonify, request
from typing import Dict, Any

from app.middleware.auth import token_required, get_current_user
from app.security.rbac import require_owner
from app.repositories.admin.roles import RolesRepository
from app.domain.models.admin_roles import (
    CreateRoleRequest,
    UpdateRoleRequest,
    CreateFromTemplateRequest,
)
from app.i18n.error_codes import ErrorCode
from app.i18n.error_codes import error_response
from pydantic import ValidationError

from .roles_core import (
    ROLE_TEMPLATES,
    format_role_response
)

# Create blueprint
roles_bp = Blueprint('admin_roles', __name__, url_prefix='/admin-panel/settings/permissions/roles')


# ============================================================================
# List & Read Endpoints
# ============================================================================

@roles_bp.route('', methods=['GET'])
@token_required
@require_owner()
def list_roles():
    """
    List all roles with filtering

    Query Parameters:
        - is_builtin (bool): Filter by builtin/system roles (false=custom)
        - hierarchy_min (int): Minimum hierarchy level
        - hierarchy_max (int): Maximum hierarchy level
        - search (str): Search in role name or display name
        - include_features (bool): Include feature assignments
        - include_permissions (bool): Include permission assignments

    Returns:
        200: List of roles
        403: Not owner-admin
    """
    try:
        # Parse query parameters
        is_builtin = request.args.get('is_builtin')
        if is_builtin is not None:
            is_builtin = is_builtin.lower() == 'true'

        hierarchy_min = request.args.get('hierarchy_min', type=int)
        hierarchy_max = request.args.get('hierarchy_max', type=int)
        search = request.args.get('search')

        # Get roles with stats
        roles = RolesRepository.find_all_with_stats(
            is_builtin=is_builtin,
            hierarchy_min=hierarchy_min,
            hierarchy_max=hierarchy_max,
            search=search
        )

        # Format response
        roles_data = [format_role_response(role, include_counts=True) for role in roles]

        return jsonify({
            'success': True,
            'data': {
                'roles': roles_data,
                'total': len(roles_data)
            }
        }), 200

    except Exception as e:
        return error_response(ErrorCode.LIST_ROLES_ERROR, 500, details={'details': str(e)})


@roles_bp.route('/<int:role_id>', methods=['GET'])
@token_required
@require_owner()
def get_role(role_id: int):
    """
    Get role details by ID

    Returns:
        200: Role details
        403: Not owner-admin
        404: Role not found
    """
    try:
        # Get role with stats
        role = RolesRepository.find_by_id_with_details(role_id)

        if not role:
            return error_response(ErrorCode.ROLE_NOT_FOUND, 404, details={'role_id': role_id})

        # Get features and permissions
        features = RolesRepository.get_role_features(role_id)
        permissions = RolesRepository.get_role_permissions(role_id)

        # Format response
        from app.api.v1.admin_panel.settings.permissions.roles_core import (
            format_feature_response,
            format_permission_response
        )

        role_data = format_role_response(role, include_counts=True)
        role_data['features'] = [format_feature_response(f) for f in features]
        role_data['permissions'] = [format_permission_response(p) for p in permissions]

        return jsonify({
            'success': True,
            'data': role_data
        }), 200

    except Exception as e:
        return error_response(ErrorCode.GET_ROLE_ERROR, 500, details={'details': str(e)})


# ============================================================================
# Create Endpoints
# ============================================================================

@roles_bp.route('', methods=['POST'])
@token_required
@require_owner()
def create_role():
    """
    Create a new custom role

    Body: CreateRoleRequest

    Returns:
        201: Role created
        400: Validation error
        403: Not owner-admin
        409: Role name already exists
    """
    try:
        # Validate request
        try:
            req_data = CreateRoleRequest(**request.json)
        except ValidationError as e:
            return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'errors': e.errors()})

        user = get_current_user()

        # Check if role name already exists
        existing = RolesRepository.find_by_name(req_data.role_name)
        if existing:
            return error_response(ErrorCode.ROLE_EXISTS, 409, details={'message': f'Role with name "{req_data.role_name}" already exists'})

        # Create role
        role = RolesRepository.create_role(
            role_name=req_data.role_name,
            display_name=req_data.display_name,
            description=req_data.description,
            hierarchy_level=req_data.hierarchy_level,
            color=req_data.color,
            icon=req_data.icon,
            created_by=user['user_id']
        )

        # Assign features if provided
        if req_data.feature_ids:
            RolesRepository.assign_features(
                role_id=role['role_id'],
                feature_ids=req_data.feature_ids,
                created_by=user['user_id'],
                replace=True
            )

        # Assign permissions if provided
        if req_data.permission_ids:
            RolesRepository.assign_permissions(
                role_id=role['role_id'],
                permission_ids=req_data.permission_ids,
                replace=True
            )

        # Get full role details
        role_detail = RolesRepository.find_by_id_with_details(role['role_id'])

        return jsonify({
            'success': True,
            'data': {
                'role_id': role_detail['role_id'],
                'role_name': role_detail['role_name'],
                'display_name': role_detail['display_name'],
                'description': role_detail['description'],
                'hierarchy_level': role_detail['hierarchy_level'],
                'color': role_detail['color'],
                'icon': role_detail['icon'],
                'is_builtin': False,
                'is_administrator': False,
                'created_at': role_detail['created_at'].isoformat(),
                'message': 'Role created successfully'
            }
        }), 201

    except Exception as e:
        return error_response(ErrorCode.CREATE_ROLE_ERROR, 500, details={'details': str(e)})


@roles_bp.route('/from-template', methods=['POST'])
@token_required
@require_owner()
def create_from_template():
    """
    Create a role from a predefined template

    Body: CreateFromTemplateRequest

    Returns:
        201: Role created from template
        400: Validation error / Invalid template
        403: Not owner-admin
        409: Role name already exists
    """
    try:
        # Validate request
        try:
            req_data = CreateFromTemplateRequest(**request.json)
        except ValidationError as e:
            return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'errors': e.errors()})

        user = get_current_user()

        # Get template
        template = ROLE_TEMPLATES.get(req_data.template)
        if not template:
            return error_response(ErrorCode.INVALID_TEMPLATE, 400, details={'message': f'Template "{req_data.template}" not found'})

        # Check if role name already exists
        existing = RolesRepository.find_by_name(req_data.role_name)
        if existing:
            return error_response(ErrorCode.ROLE_EXISTS, 409, details={'message': f'Role with name "{req_data.role_name}" already exists'})

        # Create role from template
        display_name = req_data.display_name or template['display_name']

        role = RolesRepository.create_role(
            role_name=req_data.role_name,
            display_name=display_name,
            description=template['description'],
            hierarchy_level=template['recommended_hierarchy'],
            color=template['default_color'],
            icon=template['default_icon'],
            created_by=user['user_id']
        )

        # TODO: Assign template features (need feature_code → feature_id mapping)
        # For now, use customized features if provided
        if req_data.customize_features:
            RolesRepository.assign_features(
                role_id=role['role_id'],
                feature_ids=req_data.customize_features,
                created_by=user['user_id'],
                replace=True
            )

        return jsonify({
            'success': True,
            'data': {
                'role_id': role['role_id'],
                'role_name': role['role_name'],
                'display_name': role['display_name'],
                'template': req_data.template.value,
                'message': f'Role created successfully from "{req_data.template.value}" template'
            }
        }), 201

    except Exception as e:
        return error_response(ErrorCode.CREATE_FROM_TEMPLATE_ERROR, 500, details={'details': str(e)})


# ============================================================================
# Update Endpoint
# ============================================================================

@roles_bp.route('/<int:role_id>', methods=['PUT'])
@token_required
@require_owner()
def update_role(role_id: int):
    """
    Update a custom role

    Body: UpdateRoleRequest

    Returns:
        200: Role updated
        400: Validation error
        403: Not owner-admin / Cannot update system role
        404: Role not found
    """
    try:
        # Check if role exists
        role = RolesRepository.find_by_id(role_id)
        if not role:
            return error_response(ErrorCode.ROLE_NOT_FOUND, 404, details={'message': f'Role with ID {role_id} not found'})

        # Check if role is builtin (system role) - cannot update system roles
        if role.get('is_builtin'):
            return error_response(ErrorCode.CANNOT_UPDATE_SYSTEM_ROLE, 403, details={'message': 'System roles cannot be updated'})

        # Validate request
        try:
            req_data = UpdateRoleRequest(**request.json)
        except ValidationError as e:
            return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'errors': e.errors()})

        # Update role
        updated = RolesRepository.update_role(
            role_id=role_id,
            display_name=req_data.display_name,
            description=req_data.description,
            hierarchy_level=req_data.hierarchy_level,
            color=req_data.color,
            icon=req_data.icon
        )

        if not updated:
            return error_response(ErrorCode.UPDATE_FAILED, 500, details={'message': 'Failed to update role'})

        return jsonify({
            'success': True,
            'data': {
                'role_id': updated['role_id'],
                'role_name': updated['role_name'],
                'display_name': updated['display_name'],
                'message': 'Role updated successfully'
            }
        }), 200

    except Exception as e:
        return error_response(ErrorCode.UPDATE_ROLE_ERROR, 500, details={'details': str(e)})


# ============================================================================
# Delete Endpoint
# ============================================================================

@roles_bp.route('/<int:role_id>', methods=['DELETE'])
@token_required
@require_owner()
def delete_role(role_id: int):
    """
    Delete a custom role

    Query Parameters:
        - reassign_to (int): Role ID to reassign users to (default: 'free' role)

    Returns:
        200: Role deleted
        403: Not owner-admin / Cannot delete system role
        404: Role not found
    """
    try:
        # Check if role exists
        role = RolesRepository.find_by_id(role_id)
        if not role:
            return error_response(ErrorCode.ROLE_NOT_FOUND, 404, details={'message': f'Role with ID {role_id} not found'})

        # Check if role is builtin (system role) - cannot delete system roles
        if role.get('is_builtin'):
            return error_response(ErrorCode.CANNOT_DELETE_SYSTEM_ROLE, 403, details={'message': 'System roles cannot be deleted'})

        # Get user count
        user_count = RolesRepository.get_user_count_by_role(role_id)

        # Reassign users if needed
        reassign_to_id = request.args.get('reassign_to', type=int)
        if user_count > 0:
            if not reassign_to_id:
                # Default to 'free' role
                free_role = RolesRepository.find_by_name('free')
                reassign_to_id = free_role['role_id'] if free_role else None

            if reassign_to_id:
                RolesRepository.reassign_users(role_id, reassign_to_id)
            else:
                return error_response(ErrorCode.REASSIGNMENT_REQUIRED, 400, details={'message': f'Role has {user_count} users. Provide reassign_to parameter.'})

        # Delete role
        deleted = RolesRepository.delete_role(role_id)

        if not deleted:
            return error_response(ErrorCode.DELETE_FAILED, 500, details={'message': 'Failed to delete role'})

        # Get reassign role name
        reassign_role_name = None
        if reassign_to_id:
            reassign_role = RolesRepository.find_by_id(reassign_to_id)
            reassign_role_name = reassign_role['role_name'] if reassign_role else None

        return jsonify({
            'success': True,
            'data': {
                'deleted_role_id': role_id,
                'deleted_role_name': role['role_name'],
                'affected_users': user_count,
                'reassigned_to_role': reassign_role_name,
                'message': f'Role deleted successfully. {user_count} users reassigned.'
            }
        }), 200

    except Exception as e:
        return error_response(ErrorCode.DELETE_ROLE_ERROR, 500, details={'details': str(e)})


__all__ = ['roles_bp']
