"""
RBAC 2.0 - Roles Management API

Endpoints for custom role management (Owner-Admin only).

Phase 5.3 - Owner-Admin & Dynamic Roles System
"""

from flask import Blueprint, jsonify, request
from typing import List, Dict, Optional
from datetime import datetime

from app.middleware.auth import token_required, get_current_user
from app.security.rbac import require_owner
from app.repositories.admin.roles import RolesRepository
from app.models.admin_roles import (
    CreateRoleRequest,
    UpdateRoleRequest,
    AssignFeaturesRequest,
    AssignPermissionsRequest,
    CreateFromTemplateRequest,
    RoleResponse,
    RoleDetailResponse,
    FeatureResponse,
    PermissionResponse,
    RoleTemplateResponse,
    DeleteRoleResponse,
    RoleFilterParams,
    RoleTemplate
)
from pydantic import ValidationError

# Create blueprint (registered under api_v1 which already has /api/v1 prefix)
roles_bp = Blueprint('admin_roles', __name__, url_prefix='/admin/roles')


# ============================================================================
# Role Templates Configuration
# ============================================================================

ROLE_TEMPLATES = {
    RoleTemplate.PARENT: {
        'display_name': 'Parent',
        'description': 'Parental control account for child activity monitoring',
        'recommended_hierarchy': 2,
        'default_features': ['content_approval', 'activity_reports'],
        'default_color': '#10b981',
        'default_icon': '👪'
    },
    RoleTemplate.ENTERPRISE_ADMIN: {
        'display_name': 'Enterprise Admin',
        'description': 'Enterprise administrator with bulk management features',
        'recommended_hierarchy': 6,
        'default_features': ['bulk_import', 'sso_config', 'advanced_analytics'],
        'default_color': '#3b82f6',
        'default_icon': '🏢'
    },
    RoleTemplate.AUDITOR: {
        'display_name': 'Auditor',
        'description': 'Compliance auditor with read-only access to logs and reports',
        'recommended_hierarchy': 7,
        'default_features': ['audit_logs', 'compliance_reports', 'export_data'],
        'default_color': '#8b5cf6',
        'default_icon': '🔍'
    },
    RoleTemplate.LIBRARIAN: {
        'display_name': 'Librarian',
        'description': 'Content curator for managing course catalog',
        'recommended_hierarchy': 5,
        'default_features': ['content_moderation', 'category_management'],
        'default_color': '#f59e0b',
        'default_icon': '📚'
    },
    RoleTemplate.COURSE_MANAGER: {
        'display_name': 'Course Manager',
        'description': 'Course management without full admin access',
        'recommended_hierarchy': 4,
        'default_features': ['course_crud', 'course_publishing', 'course_analytics'],
        'default_color': '#06b6d4',
        'default_icon': '🎓'
    }
}


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
        roles_data = []
        for role in roles:
            role_data = {
                'role_id': role['role_id'],
                'role_name': role['role_name'],
                'display_name': role['display_name'],
                'description': role['description'],
                'hierarchy_level': role['hierarchy_level'],
                'color': role['color'],
                'icon': role['icon'],
                'is_builtin': role['is_builtin'],
                'is_administrator': role['is_administrator'],
                'created_at': role['created_at'].isoformat() if role['created_at'] else None,
                'updated_at': role['updated_at'].isoformat() if role['updated_at'] else None,
                'created_by': str(role['created_by']) if role.get('created_by') else None,
                'feature_count': role.get('feature_count', 0),
                'permission_count': role.get('permission_count', 0),
                'user_count': role.get('user_count', 0)
            }
            roles_data.append(role_data)

        return jsonify({
            'success': True,
            'data': {
                'roles': roles_data,
                'total': len(roles_data)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'LIST_ROLES_ERROR',
                'message': f'Failed to list roles: {str(e)}'
            }
        }), 500


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
            return jsonify({
                'success': False,
                'error': {
                    'code': 'ROLE_NOT_FOUND',
                    'message': f'Role with ID {role_id} not found'
                }
            }), 404

        # Get features and permissions
        features = RolesRepository.get_role_features(role_id)
        permissions = RolesRepository.get_role_permissions(role_id)

        # Format response
        role_data = {
            'role_id': role['role_id'],
            'role_name': role['role_name'],
            'display_name': role['display_name'],
            'description': role['description'],
            'hierarchy_level': role['hierarchy_level'],
            'color': role['color'],
            'icon': role['icon'],
            'is_builtin': role['is_builtin'],
            'is_administrator': role['is_administrator'],
            'created_at': role['created_at'].isoformat() if role['created_at'] else None,
            'updated_at': role['updated_at'].isoformat() if role['updated_at'] else None,
            'created_by': str(role['created_by']) if role.get('created_by') else None,
            'feature_count': role.get('feature_count', 0),
            'permission_count': role.get('permission_count', 0),
            'user_count': role.get('user_count', 0),
            'features': [
                {
                    'feature_id': f['feature_id'],
                    'feature_code': f['feature_code'],
                    'feature_name': f['feature_name'],
                    'category': f['category'],
                    'active': f['active'],
                    'enabled_for_role': f['enabled_for_role']
                }
                for f in features
            ],
            'permissions': [
                {
                    'permission_id': p['permission_id'],
                    'permission_key': p['permission_key'],
                    'display_name': p.get('display_name'),
                    'description': p.get('description'),
                    'module': p.get('module'),
                    'category': p.get('category')
                }
                for p in permissions
            ]
        }

        return jsonify({
            'success': True,
            'data': role_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_ROLE_ERROR',
                'message': f'Failed to get role: {str(e)}'
            }
        }), 500


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
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Invalid request data',
                    'details': e.errors()
                }
            }), 400

        user = get_current_user()

        # Check if role name already exists
        existing = RolesRepository.find_by_name(req_data.role_name)
        if existing:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'ROLE_EXISTS',
                    'message': f'Role with name "{req_data.role_name}" already exists'
                }
            }), 409

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
        return jsonify({
            'success': False,
            'error': {
                'code': 'CREATE_ROLE_ERROR',
                'message': f'Failed to create role: {str(e)}'
            }
        }), 500


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
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Invalid request data',
                    'details': e.errors()
                }
            }), 400

        user = get_current_user()

        # Get template
        template = ROLE_TEMPLATES.get(req_data.template)
        if not template:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_TEMPLATE',
                    'message': f'Template "{req_data.template}" not found'
                }
            }), 400

        # Check if role name already exists
        existing = RolesRepository.find_by_name(req_data.role_name)
        if existing:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'ROLE_EXISTS',
                    'message': f'Role with name "{req_data.role_name}" already exists'
                }
            }), 409

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
        return jsonify({
            'success': False,
            'error': {
                'code': 'CREATE_FROM_TEMPLATE_ERROR',
                'message': f'Failed to create role from template: {str(e)}'
            }
        }), 500


# ============================================================================
# Update Endpoints
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
            return jsonify({
                'success': False,
                'error': {
                    'code': 'ROLE_NOT_FOUND',
                    'message': f'Role with ID {role_id} not found'
                }
            }), 404

        # Check if role is builtin (system role) - cannot update system roles
        if role.get('is_builtin'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CANNOT_UPDATE_SYSTEM_ROLE',
                    'message': 'System roles cannot be updated'
                }
            }), 403

        # Validate request
        try:
            req_data = UpdateRoleRequest(**request.json)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Invalid request data',
                    'details': e.errors()
                }
            }), 400

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
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UPDATE_FAILED',
                    'message': 'Failed to update role'
                }
            }), 500

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
        return jsonify({
            'success': False,
            'error': {
                'code': 'UPDATE_ROLE_ERROR',
                'message': f'Failed to update role: {str(e)}'
            }
        }), 500


@roles_bp.route('/<int:role_id>/features', methods=['POST'])
@token_required
@require_owner()
def assign_features(role_id: int):
    """
    Assign features to a role

    Body: AssignFeaturesRequest

    Returns:
        200: Features assigned
        400: Validation error
        403: Not owner-admin
        404: Role not found
    """
    try:
        # Check if role exists
        role = RolesRepository.find_by_id(role_id)
        if not role:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'ROLE_NOT_FOUND',
                    'message': f'Role with ID {role_id} not found'
                }
            }), 404

        # Validate request
        try:
            req_data = AssignFeaturesRequest(**request.json)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Invalid request data',
                    'details': e.errors()
                }
            }), 400

        user = get_current_user()

        # Assign features
        count = RolesRepository.assign_features(
            role_id=role_id,
            feature_ids=req_data.feature_ids,
            created_by=user['user_id'],
            replace=req_data.replace
        )

        return jsonify({
            'success': True,
            'data': {
                'role_id': role_id,
                'features_assigned': count,
                'mode': 'replace' if req_data.replace else 'add',
                'message': f'{count} features assigned successfully'
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'ASSIGN_FEATURES_ERROR',
                'message': f'Failed to assign features: {str(e)}'
            }
        }), 500


@roles_bp.route('/<int:role_id>/permissions', methods=['POST'])
@token_required
@require_owner()
def assign_permissions(role_id: int):
    """
    Assign permissions to a role

    Body: AssignPermissionsRequest

    Returns:
        200: Permissions assigned
        400: Validation error
        403: Not owner-admin
        404: Role not found
    """
    try:
        # Check if role exists
        role = RolesRepository.find_by_id(role_id)
        if not role:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'ROLE_NOT_FOUND',
                    'message': f'Role with ID {role_id} not found'
                }
            }), 404

        # Validate request
        try:
            req_data = AssignPermissionsRequest(**request.json)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Invalid request data',
                    'details': e.errors()
                }
            }), 400

        # Assign permissions
        count = RolesRepository.assign_permissions(
            role_id=role_id,
            permission_ids=req_data.permission_ids,
            replace=req_data.replace
        )

        return jsonify({
            'success': True,
            'data': {
                'role_id': role_id,
                'permissions_assigned': count,
                'mode': 'replace' if req_data.replace else 'add',
                'message': f'{count} permissions assigned successfully'
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'ASSIGN_PERMISSIONS_ERROR',
                'message': f'Failed to assign permissions: {str(e)}'
            }
        }), 500


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
            return jsonify({
                'success': False,
                'error': {
                    'code': 'ROLE_NOT_FOUND',
                    'message': f'Role with ID {role_id} not found'
                }
            }), 404

        # Check if role is builtin (system role) - cannot delete system roles
        if role.get('is_builtin'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CANNOT_DELETE_SYSTEM_ROLE',
                    'message': 'System roles cannot be deleted'
                }
            }), 403

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
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'REASSIGNMENT_REQUIRED',
                        'message': f'Role has {user_count} users. Provide reassign_to parameter.'
                    }
                }), 400

        # Delete role
        deleted = RolesRepository.delete_role(role_id)

        if not deleted:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'DELETE_FAILED',
                    'message': 'Failed to delete role'
                }
            }), 500

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
        return jsonify({
            'success': False,
            'error': {
                'code': 'DELETE_ROLE_ERROR',
                'message': f'Failed to delete role: {str(e)}'
            }
        }), 500


# ============================================================================
# Templates Endpoint
# ============================================================================

@roles_bp.route('/templates', methods=['GET'])
@token_required
@require_owner()
def get_templates():
    """
    Get available role templates

    Returns:
        200: List of templates
        403: Not owner-admin
    """
    try:
        templates_data = []
        for template_key, template_config in ROLE_TEMPLATES.items():
            templates_data.append({
                'template': template_key.value,
                'display_name': template_config['display_name'],
                'description': template_config['description'],
                'recommended_hierarchy': template_config['recommended_hierarchy'],
                'default_features': template_config['default_features'],
                'default_color': template_config['default_color'],
                'default_icon': template_config['default_icon']
            })

        return jsonify({
            'success': True,
            'data': {
                'templates': templates_data,
                'total': len(templates_data)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_TEMPLATES_ERROR',
                'message': f'Failed to get templates: {str(e)}'
            }
        }), 500


# ============================================================================
# System Features & Permissions Endpoints
# ============================================================================

@roles_bp.route('/permissions', methods=['GET'])
@token_required
@require_owner()
def get_all_permissions():
    """
    Get list of all available permissions in the system.

    This endpoint returns all permission keys that can be assigned to roles.

    Returns:
        200: List of all permissions
        403: Not owner-admin
        500: Server error
    """
    try:
        # Get all permissions from repository
        permissions = RolesRepository.get_all_available_permissions()

        # Format response
        permissions_data = []
        for perm in permissions:
            permissions_data.append({
                'permission_key': perm['permission_key'],
                'description': perm.get('description', ''),
                'category': perm.get('category', 'general')
            })

        return jsonify({
            'success': True,
            'data': permissions_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_PERMISSIONS_ERROR',
                'message': f'Failed to get permissions: {str(e)}'
            }
        }), 500


@roles_bp.route('/system-features', methods=['GET'])
@token_required
@require_owner()
def get_system_features():
    """
    Get list of all system features (25 System-Features).

    Returns features from support_systems.system_features table.

    Returns:
        200: List of all system features
        403: Not owner-admin
        500: Server error
    """
    try:
        # Get all system features from repository
        features = RolesRepository.get_all_system_features()

        # Format response
        features_data = []
        for feature in features:
            features_data.append({
                'feature_code': feature['feature_code'],
                'feature_name': feature['feature_name'],
                'description': feature.get('description', ''),
                'category': feature.get('category', 'general'),
                'icon': feature.get('icon', ''),
                'requires_infrastructure': feature.get('requires_infrastructure', False),
                'requires_external_service': feature.get('requires_external_service', False)
            })

        return jsonify({
            'success': True,
            'data': features_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_SYSTEM_FEATURES_ERROR',
                'message': f'Failed to get system features: {str(e)}'
            }
        }), 500


# Export blueprint
__all__ = ['roles_bp']
