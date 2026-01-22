"""
Role Studio Modes API

Endpoints for managing dynamic role-to-studio-mode configurations.
Allows Owner-Admin to configure which studio modes roles have access to.

Phase 2 - Owner-Admin Dynamic Configuration
"""

from flask import Blueprint, jsonify, request
from typing import Optional
from datetime import datetime

from app.api.middleware.auth import token_required, get_current_user
from app.infrastructure.security.rbac import require_owner
from app.application.services.role_studio_service import RoleStudioService
from app.domain.models.role_studio import (
    CreateRoleStudioRequest,
    UpdateRoleStudioRequest,
    UpdateRolePermissionsRequest,
    DeactivateRoleRequest,
    RoleStudioResponse,
    RoleStudioListResponse,
    RoleStudioDetailResponse,
    RoleChangeHistoryResponse,
    PermissionsResponse,
    StudioConfigResponse,
    SuccessResponse,
    ErrorResponse
)
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response
from pydantic import ValidationError
import json

# Create blueprint
role_studio_bp = Blueprint('admin_role_studio', __name__, url_prefix='/admin-panel/role-studio')


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_user_id_for_audit():
    """Get current user ID for audit logging"""
    try:
        user = get_current_user()
        return user.get('user_id', 'system')
    except:
        return 'system'


# ============================================================================
# RETRIEVE ROLE STUDIO MODES
# ============================================================================

@role_studio_bp.route('/modes', methods=['GET'])
@token_required
def get_all_modes():
    """
    Get all available role studio modes

    Query Parameters:
        - active_only: Boolean (default: true) - Only return active modes
        - limit: Integer (default: 100) - Max results per page
        - offset: Integer (default: 0) - Pagination offset

    Returns:
        200: List of role studio modes
        401: Unauthorized
    """
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))

        if active_only:
            modes = RoleStudioService.get_all_active_roles()
        else:
            modes = RoleStudioService.get_all_active_roles()  # For now, return active

        # Apply pagination
        total = len(modes)
        modes = modes[offset:offset + limit]

        response_data = {
            'data': modes,
            'total': total,
            'limit': limit,
            'offset': offset
        }

        return jsonify(response_data), 200

    except Exception as e:
        return error_response(ErrorCode.INTERNAL_ERROR, 500, details={'details': str(e)})


@role_studio_bp.route('/modes/<role_code>', methods=['GET'])
@token_required
def get_mode(role_code: str):
    """
    Get specific role studio mode configuration

    Path Parameters:
        - role_code: The role code

    Returns:
        200: Role studio mode configuration
        404: Role not found
        401: Unauthorized
    """
    try:
        mode = RoleStudioService.get_role_studio_mode(role_code)

        if not mode:
            return error_response(ErrorCode.NOT_FOUND, 404, details={'message': f'Role studio mode not found: {role_code}'})

        # Calculate permission count
        permissions = mode.get('permissions', {})
        if isinstance(permissions, str):
            try:
                permissions = json.loads(permissions)
            except:
                permissions = {}

        mode['permission_count'] = len(permissions)

        return jsonify(mode), 200

    except Exception as e:
        return error_response(ErrorCode.INTERNAL_ERROR, 500, details={'details': str(e)})


@role_studio_bp.route('/studio-modes', methods=['GET'])
@token_required
def get_modes_by_studio(studio_mode: Optional[str] = None):
    """
    Get all roles for a specific studio mode

    Query Parameters:
        - studio_mode: The studio mode to filter by

    Returns:
        200: List of roles assigned to that studio mode
        400: Bad request (missing studio_mode parameter)
    """
    try:
        studio_mode = request.args.get('studio_mode')

        if not studio_mode:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'studio_mode parameter is required'
                }
            }), 400

        roles = RoleStudioService.get_roles_by_studio_mode(studio_mode)

        return jsonify({
            'data': roles,
            'total': len(roles)
        }), 200

    except Exception as e:
        return error_response(ErrorCode.INTERNAL_ERROR, 500, details={'details': str(e)})


@role_studio_bp.route('/organization-roles', methods=['GET'])
@token_required
def get_organization_roles():
    """
    Get all roles that require organization membership

    Returns:
        200: List of organization-required roles
    """
    try:
        roles = RoleStudioService.get_organization_required_roles()
        return jsonify({
            'data': roles,
            'total': len(roles)
        }), 200

    except Exception as e:
        return error_response(ErrorCode.INTERNAL_ERROR, 500, details={'details': str(e)})


# ============================================================================
# PERMISSION MANAGEMENT
# ============================================================================

@role_studio_bp.route('/modes/<role_code>/permissions', methods=['GET'])
@token_required
def get_permissions(role_code: str):
    """
    Get all permissions for a specific role

    Path Parameters:
        - role_code: The role code

    Returns:
        200: Permissions dictionary
        404: Role not found
    """
    try:
        permissions = RoleStudioService.get_role_permissions(role_code)

        if not permissions:
            return error_response(ErrorCode.NOT_FOUND, 404, details={'message': f'Role not found: {role_code}'})

        return jsonify({
            'role_code': role_code,
            'permissions': permissions,
            'permission_count': len(permissions)
        }), 200

    except Exception as e:
        return error_response(ErrorCode.INTERNAL_ERROR, 500, details={'details': str(e)})


@role_studio_bp.route('/modes/<role_code>/permissions', methods=['PUT'])
@token_required
@require_owner
def update_permissions(role_code: str):
    """
    Update permissions for a role (Owner-Admin only)

    Path Parameters:
        - role_code: The role code

    Request Body:
        - permissions: Dictionary of permission flags
        - change_reason: Optional reason for the change (for audit trail)

    Returns:
        200: Updated permissions
        400: Validation error
        404: Role not found
        403: Forbidden (must be Owner-Admin)
    """
    try:
        data = request.get_json()
        request_model = UpdateRolePermissionsRequest(**data)

        user_id = get_user_id_for_audit()

        updated_role = RoleStudioService.update_permissions(
            role_code=role_code,
            permissions=request_model.permissions,
            changed_by=user_id,
            change_reason=request_model.change_reason
        )

        if not updated_role:
            return error_response(ErrorCode.NOT_FOUND, 404, details={'message': f'Role not found: {role_code}'})

        return jsonify({
            'success': True,
            'data': updated_role
        }), 200

    except ValidationError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'errors': e.errors()})

    except Exception as e:
        return error_response(ErrorCode.INTERNAL_ERROR, 500, details={'details': str(e)})


# ============================================================================
# ROLE MANAGEMENT (Owner-Admin only)
# ============================================================================

@role_studio_bp.route('/modes', methods=['POST'])
@token_required
@require_owner
def create_mode():
    """
    Create new role studio mode (Owner-Admin only)

    Request Body:
        - role_code: Unique role identifier (required)
        - display_name: Human-readable name (required)
        - studio_mode: Studio mode (required)
        - permissions: Permission dictionary (optional)
        - requires_organization: Boolean (optional)
        - description: Text description (optional)

    Returns:
        201: Created role studio mode
        400: Validation error
        409: Role already exists
        403: Forbidden (must be Owner-Admin)
    """
    try:
        data = request.get_json()
        request_model = CreateRoleStudioRequest(**data)

        created = RoleStudioService.create_role(
            role_code=request_model.role_code,
            display_name=request_model.display_name,
            studio_mode=request_model.studio_mode.value,
            permissions=request_model.permissions,
            requires_organization=request_model.requires_organization,
            description=request_model.description
        )

        return jsonify({
            'success': True,
            'data': created
        }), 201

    except ValidationError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'errors': e.errors()})

    except ValueError as e:
        return error_response(ErrorCode.CONFLICT, 409, details={'message': str(e)})

    except Exception as e:
        return error_response(ErrorCode.INTERNAL_ERROR, 500, details={'details': str(e)})


@role_studio_bp.route('/modes/<role_code>', methods=['PUT'])
@token_required
@require_owner
def update_mode(role_code: str):
    """
    Update role studio mode (Owner-Admin only)

    Path Parameters:
        - role_code: The role code

    Request Body:
        - Fields to update (all optional)

    Returns:
        200: Updated role studio mode
        400: Validation error
        404: Role not found
        403: Forbidden (must be Owner-Admin)
    """
    try:
        data = request.get_json()
        request_model = UpdateRoleStudioRequest(**data)

        user_id = get_user_id_for_audit()

        # Prepare update data (only include non-None values)
        updates = {}
        if request_model.display_name:
            updates['display_name'] = request_model.display_name
        if request_model.studio_mode:
            updates['studio_mode'] = request_model.studio_mode.value
        if request_model.permissions is not None:
            updates['permissions'] = request_model.permissions
        if request_model.requires_organization is not None:
            updates['requires_organization'] = request_model.requires_organization
        if request_model.is_active is not None:
            updates['is_active'] = request_model.is_active
        if request_model.description is not None:
            updates['description'] = request_model.description

        updated = RoleStudioService.update_role(
            role_code=role_code,
            updates=updates,
            changed_by=user_id,
            change_reason=request_model.description if 'description' in request_model else None
        )

        if not updated:
            return error_response(ErrorCode.NOT_FOUND, 404, details={'message': f'Role not found: {role_code}'})

        return jsonify({
            'success': True,
            'data': updated
        }), 200

    except ValidationError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'errors': e.errors()})

    except Exception as e:
        return error_response(ErrorCode.INTERNAL_ERROR, 500, details={'details': str(e)})


@role_studio_bp.route('/modes/<role_code>', methods=['DELETE'])
@token_required
@require_owner
def delete_mode(role_code: str):
    """
    Deactivate role studio mode (soft delete - Owner-Admin only)

    Path Parameters:
        - role_code: The role code

    Request Body (optional):
        - change_reason: Reason for deactivation

    Returns:
        200: Deactivated role
        404: Role not found
        403: Forbidden (must be Owner-Admin)
    """
    try:
        data = request.get_json() or {}

        user_id = get_user_id_for_audit()

        deactivated = RoleStudioService.deactivate_role(
            role_code=role_code,
            changed_by=user_id,
            change_reason=data.get('change_reason')
        )

        if not deactivated:
            return error_response(ErrorCode.NOT_FOUND, 404, details={'message': f'Role not found: {role_code}'})

        return jsonify({
            'success': True,
            'data': deactivated,
            'message': f'Role {role_code} has been deactivated'
        }), 200

    except Exception as e:
        return error_response(ErrorCode.INTERNAL_ERROR, 500, details={'details': str(e)})


# ============================================================================
# AUDIT TRAIL
# ============================================================================

@role_studio_bp.route('/modes/<role_code>/history', methods=['GET'])
@token_required
def get_change_history(role_code: str):
    """
    Get change history for a role (audit trail)

    Path Parameters:
        - role_code: The role code

    Query Parameters:
        - limit: Maximum history records (default: 50)

    Returns:
        200: List of change history records
        404: Role not found (or no history available)
    """
    try:
        limit = int(request.args.get('limit', 50))

        history = RoleStudioService.get_role_change_history(role_code, limit=limit)

        if not history:
            return jsonify({
                'data': [],
                'total': 0,
                'message': f'No change history found for role {role_code}'
            }), 200

        return jsonify({
            'data': history,
            'total': len(history)
        }), 200

    except Exception as e:
        return error_response(ErrorCode.INTERNAL_ERROR, 500, details={'details': str(e)})
