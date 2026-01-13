"""
Admin API for Learning Method Plugins
8 endpoints for plugin discovery, approval, and management.
"""
from flask import request, jsonify, g
from app.api import api_v1
from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.services.plugins.lm_discovery import LMPluginDiscoveryService
from app.services.plugins.lm_registry import force_reload_registry
from app.repositories.plugins.lm_plugins import LMPluginRepository
from app.extensions import limiter


@api_v1.route('/admin/plugins/learning-methods/scan', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
@limiter.limit("10 per minute")
def scan_plugins():
    """
    Trigger plugin discovery scan.
    Rate limit: 1 request per 5 minutes.
    """
    user_id = g.current_user['user_id']

    # Discover plugins
    discovered = LMPluginDiscoveryService.scan_plugins()

    # Register each discovered plugin
    registered = []
    for metadata in discovered:
        plugin_id = LMPluginDiscoveryService.register_plugin(metadata, user_id)
        if plugin_id:
            registered.append(plugin_id)

    return jsonify({
        'success': True,
        'data': {
            'discovered_count': len(discovered),
            'registered_count': len(registered),
            'registered_ids': registered
        }
    }), 200


@api_v1.route('/admin/plugins/learning-methods/pending', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
@limiter.limit("100 per minute")
def get_pending_plugins():
    """Get all plugins pending review."""
    plugins = LMPluginRepository.get_pending_plugins()

    return jsonify({
        'success': True,
        'data': plugins
    }), 200


@api_v1.route('/admin/plugins/learning-methods/<plugin_id>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
@limiter.limit("100 per minute")
def get_plugin_detail(plugin_id: str):
    """Get plugin detail by ID."""
    plugin = LMPluginRepository.find_by_id(plugin_id)

    if not plugin:
        return jsonify({
            'success': False,
            'error': {'code': 'NOT_FOUND', 'message': 'Plugin not found'}
        }), 404

    return jsonify({
        'success': True,
        'data': plugin
    }), 200


@api_v1.route('/admin/plugins/learning-methods/<plugin_id>/approve', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
@limiter.limit("100 per minute")
def approve_plugin(plugin_id: str):
    """Approve a pending plugin."""
    user_id = g.current_user['user_id']

    success = LMPluginRepository.approve_plugin(plugin_id, user_id)

    if not success:
        return jsonify({
            'success': False,
            'error': {'code': 'APPROVAL_FAILED', 'message': 'Plugin not found or not pending'}
        }), 400

    return jsonify({
        'success': True,
        'data': {'plugin_id': plugin_id, 'status': 'approved'}
    }), 200


@api_v1.route('/admin/plugins/learning-methods/<plugin_id>/reject', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
@limiter.limit("100 per minute")
def reject_plugin(plugin_id: str):
    """Reject a pending plugin."""
    user_id = g.current_user['user_id']
    data = request.get_json()
    reason = data.get('reason', '')

    success = LMPluginRepository.reject_plugin(plugin_id, user_id, reason)

    if not success:
        return jsonify({
            'success': False,
            'error': {'code': 'REJECTION_FAILED', 'message': 'Plugin not found'}
        }), 400

    return jsonify({
        'success': True,
        'data': {'plugin_id': plugin_id, 'status': 'rejected'}
    }), 200


@api_v1.route('/admin/plugins/learning-methods/<plugin_id>/activate', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
@limiter.limit("100 per minute")
def activate_plugin(plugin_id: str):
    """Activate an approved plugin."""
    user_id = g.current_user['user_id']

    success = LMPluginRepository.activate_plugin(plugin_id, user_id)

    if not success:
        return jsonify({
            'success': False,
            'error': {'code': 'ACTIVATION_FAILED', 'message': 'Plugin not approved or not found'}
        }), 400

    # Force registry reload to pick up newly activated plugin
    force_reload_registry()

    return jsonify({
        'success': True,
        'data': {'plugin_id': plugin_id, 'status': 'active'}
    }), 200


@api_v1.route('/admin/plugins/learning-methods/<plugin_id>/deactivate', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
@limiter.limit("100 per minute")
def deactivate_plugin(plugin_id: str):
    """Deactivate an active plugin."""
    user_id = g.current_user['user_id']

    # Check if plugin is in use
    if LMPluginRepository.is_plugin_in_use(plugin_id):
        return jsonify({
            'success': False,
            'error': {'code': 'IN_USE', 'message': 'Cannot deactivate plugin that is in use'}
        }), 400

    success = LMPluginRepository.deactivate_plugin(plugin_id, user_id)

    if not success:
        return jsonify({
            'success': False,
            'error': {'code': 'DEACTIVATION_FAILED', 'message': 'Plugin not found'}
        }), 400

    # Force registry reload to remove deactivated plugin
    force_reload_registry()

    return jsonify({
        'success': True,
        'data': {'plugin_id': plugin_id, 'status': 'inactive'}
    }), 200


@api_v1.route('/admin/plugins/learning-methods/active', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
@limiter.limit("100 per minute")
def get_active_plugins():
    """Get all active plugins."""
    plugins = LMPluginRepository.get_active_plugins()

    return jsonify({
        'success': True,
        'data': plugins
    }), 200
