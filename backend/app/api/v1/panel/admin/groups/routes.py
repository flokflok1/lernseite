"""
Admin Groups API - Group CRUD & Permissions Registry

Admin endpoints for managing authorization groups.
Replaces legacy RBAC with flexible group-based authorization.

Endpoints (this file):
- GET /admin/groups - List all groups
- POST /admin/groups - Create new group
- GET /admin/groups/<id> - Get group details
- PUT /admin/groups/<id> - Update group
- DELETE /admin/groups/<id> - Delete group
- GET /admin/groups/permissions/registry - List all available permissions

Member and permission endpoints are in routes_part2.py.

ISO 27001:2013 compliant - Admin-only endpoints
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from flask import Blueprint, jsonify, request
from typing import Dict, Any, Tuple, Optional
import logging

from app.setup.initialization.groups import GroupSetup
from app.api.middleware.auth import token_required, admin_required
from app.infrastructure.persistence.repositories.group.admin_queries import GroupAdminQueryRepository

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
    result = GroupAdminQueryRepository.get_group_by_id(group_id)
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

    result = GroupAdminQueryRepository.update_group(group_id, updates, params)

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
    return GroupAdminQueryRepository.delete_group(group_id) is not None


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

        permissions = GroupAdminQueryRepository.get_all_permissions(category)
        categories = GroupAdminQueryRepository.get_permission_categories()

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


# Members and permissions endpoints are in routes_part2.py
# They are registered on the same blueprint via import side-effect
import app.api.v1.panel.admin.groups.routes_part2  # noqa: F401, E402


__all__ = ['bp']
