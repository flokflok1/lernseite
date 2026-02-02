"""
Admin API - Permission Thresholds Management

Allows admins to configure hierarchy thresholds for permissions in real-time
without code changes (RBAC 2.0).

Endpoints:
- GET /admin/settings/permissions/thresholds - List all thresholds
- PUT /admin/settings/permissions/thresholds/<key> - Update threshold
- GET /admin/settings/permissions/audit - View audit log
"""

from flask import Blueprint, jsonify, request, g
from typing import Dict, Any

from app.api.middleware.auth import admin_required
from app.application.services.permission_service import PermissionService
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query

# Create blueprint
permission_thresholds_bp = Blueprint('permission_thresholds', __name__, url_prefix='/admin-panel/settings/permissions')


@permission_thresholds_bp.route('/thresholds', methods=['GET'])
@admin_required
def list_thresholds():
    """
    List all permission thresholds.

    Response:
        200: List of thresholds
        500: Server error

    Example response:
        {
            "success": true,
            "thresholds": [
                {
                    "threshold_id": 1,
                    "permission_key": "courses.edit_any",
                    "min_hierarchy_level": 8,
                    "description": "Edit any course regardless of creator",
                    "is_active": true
                },
                ...
            ]
        }
    """
    try:
        thresholds = PermissionService.get_all_thresholds()

        return jsonify({
            'success': True,
            'thresholds': thresholds,
            'count': len(thresholds)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch thresholds',
            'details': str(e)
        }), 500


@permission_thresholds_bp.route('/thresholds/<permission_key>', methods=['GET'])
@admin_required
def get_threshold(permission_key: str):
    """
    Get specific permission threshold.

    Args:
        permission_key: Permission key (e.g., 'courses.edit_any')

    Response:
        200: Threshold found
        404: Threshold not found
        500: Server error
    """
    try:
        result = fetch_one(
            """
            SELECT
                threshold_id,
                permission_key,
                min_hierarchy_level,
                description,
                is_active,
                created_at,
                updated_at
            FROM core.permission_thresholds
            WHERE permission_key = %s
            """,
            (permission_key,)
        )

        if not result:
            return jsonify({
                'success': False,
                'error': 'Threshold not found',
                'permission_key': permission_key
            }), 404

        return jsonify({
            'success': True,
            'threshold': result
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch threshold',
            'details': str(e)
        }), 500


@permission_thresholds_bp.route('/thresholds/<permission_key>', methods=['PUT'])
@admin_required
def update_threshold(permission_key: str):
    """
    Update permission threshold.

    Args:
        permission_key: Permission key to update

    Request body:
        {
            "min_hierarchy_level": 6
        }

    Response:
        200: Threshold updated successfully
        400: Invalid input
        404: Threshold not found
        500: Server error

    Example:
        PUT /admin/permissions/thresholds/courses.edit_any
        {"min_hierarchy_level": 6}

        Makes courses.edit_any available to moderator+ (instead of admin+)
    """
    try:
        data = request.get_json()

        if not data or 'min_hierarchy_level' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: min_hierarchy_level'
            }), 400

        new_level = data['min_hierarchy_level']

        # Validate level
        try:
            new_level = int(new_level)
            if not (1 <= new_level <= 10):
                raise ValueError()
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'min_hierarchy_level must be integer between 1 and 10'
            }), 400

        # Check if threshold exists
        existing = fetch_one(
            "SELECT threshold_id, min_hierarchy_level FROM core.permission_thresholds WHERE permission_key = %s",
            (permission_key,)
        )

        if not existing:
            return jsonify({
                'success': False,
                'error': 'Threshold not found',
                'permission_key': permission_key
            }), 404

        old_level = existing['min_hierarchy_level']

        # No change needed
        if old_level == new_level:
            return jsonify({
                'success': True,
                'message': 'Threshold already at requested level',
                'permission_key': permission_key,
                'min_hierarchy_level': new_level
            }), 200

        # Update threshold
        user = g.current_user
        user_id = user.get('user_id')

        success = PermissionService.update_threshold(permission_key, new_level, user_id)

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to update threshold'
            }), 500

        return jsonify({
            'success': True,
            'message': 'Threshold updated successfully',
            'permission_key': permission_key,
            'old_level': old_level,
            'new_level': new_level
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to update threshold',
            'details': str(e)
        }), 500


@permission_thresholds_bp.route('/thresholds/<permission_key>/toggle', methods=['POST'])
@admin_required
def toggle_threshold(permission_key: str):
    """
    Toggle permission threshold active status.

    Args:
        permission_key: Permission key to toggle

    Response:
        200: Threshold toggled successfully
        404: Threshold not found
        500: Server error
    """
    try:
        # Get current status
        result = fetch_one(
            "SELECT threshold_id, is_active FROM core.permission_thresholds WHERE permission_key = %s",
            (permission_key,)
        )

        if not result:
            return jsonify({
                'success': False,
                'error': 'Threshold not found',
                'permission_key': permission_key
            }), 404

        new_status = not result['is_active']

        # Update status
        execute_query(
            """
            UPDATE core.permission_thresholds
            SET is_active = %s, updated_at = NOW()
            WHERE permission_key = %s
            """,
            (new_status, permission_key)
        )

        # Invalidate cache
        PermissionService.invalidate_threshold_cache(permission_key)

        return jsonify({
            'success': True,
            'message': f"Threshold {'activated' if new_status else 'deactivated'}",
            'permission_key': permission_key,
            'is_active': new_status
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to toggle threshold',
            'details': str(e)
        }), 500


@permission_thresholds_bp.route('/audit', methods=['GET'])
@admin_required
def get_audit_log():
    """
    Get permission threshold audit log.

    Query params:
        - limit: Max results (default: 50)
        - permission_key: Filter by permission key (optional)

    Response:
        200: Audit log entries
        500: Server error

    Example response:
        {
            "success": true,
            "audit_log": [
                {
                    "audit_id": 1,
                    "permission_key": "courses.edit_any",
                    "old_min_level": 8,
                    "new_min_level": 6,
                    "changed_by": "admin@lsx.de",
                    "changed_at": "2026-01-12T14:30:00Z",
                    "action": "updated"
                },
                ...
            ]
        }
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        permission_key = request.args.get('permission_key')

        # Build query
        query = """
            SELECT
                a.audit_id,
                a.threshold_id,
                a.permission_key,
                a.old_min_level,
                a.new_min_level,
                a.action,
                a.changed_at,
                u.email as changed_by
            FROM core.permission_threshold_audit a
            LEFT JOIN core.users u ON a.changed_by_user_id = u.user_id
        """
        params = []

        if permission_key:
            query += " WHERE a.permission_key = %s"
            params.append(permission_key)

        query += " ORDER BY a.changed_at DESC LIMIT %s"
        params.append(limit)

        results = fetch_all(query, tuple(params))

        return jsonify({
            'success': True,
            'audit_log': results or [],
            'count': len(results) if results else 0
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch audit log',
            'details': str(e)
        }), 500


@permission_thresholds_bp.route('/cache/invalidate', methods=['POST'])
@admin_required
def invalidate_cache():
    """
    Invalidate permission threshold cache.

    Request body (optional):
        {
            "permission_key": "courses.edit_any"  # Specific key, or omit for all
        }

    Response:
        200: Cache invalidated successfully
        500: Server error
    """
    try:
        data = request.get_json() or {}
        permission_key = data.get('permission_key')

        PermissionService.invalidate_threshold_cache(permission_key)

        return jsonify({
            'success': True,
            'message': f"Cache invalidated for {'all permissions' if not permission_key else permission_key}"
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to invalidate cache',
            'details': str(e)
        }), 500


# Export blueprint
__all__ = ['permission_thresholds_bp']
