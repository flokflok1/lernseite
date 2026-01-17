"""
RBAC 2.0 - Roles Features & Permissions Management

Endpoints for assigning features and permissions to roles, plus system features/permissions listing.

Phase 5.3 - Owner-Admin & Dynamic Roles System
"""

from flask import Blueprint, jsonify, request

from app.middleware.auth import token_required
from app.security.rbac import require_owner
from app.repositories.admin.roles import RolesRepository
from app.models.admin_roles import (
    AssignFeaturesRequest,
    AssignPermissionsRequest,
)
from app.middleware.auth import get_current_user
from pydantic import ValidationError

from .roles_core import (
    ROLE_TEMPLATES,
    format_feature_response,
    format_permission_response
)

# Create blueprint
roles_mgmt_bp = Blueprint('admin_roles_management', __name__, url_prefix='/admin-panel/settings/permissions/roles')


# ============================================================================
# Features Assignment Endpoint
# ============================================================================

@roles_mgmt_bp.route('/<int:role_id>/features', methods=['POST'])
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


# ============================================================================
# Permissions Assignment Endpoint
# ============================================================================

@roles_mgmt_bp.route('/<int:role_id>/permissions', methods=['POST'])
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
# Templates Endpoint
# ============================================================================

@roles_mgmt_bp.route('/templates', methods=['GET'])
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
# System Permissions Endpoint
# ============================================================================

@roles_mgmt_bp.route('/permissions', methods=['GET'])
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


# ============================================================================
# System Features Endpoint
# ============================================================================

@roles_mgmt_bp.route('/system-features', methods=['GET'])
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


__all__ = ['roles_mgmt_bp']
