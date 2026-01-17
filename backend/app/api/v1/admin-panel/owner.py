"""
Owner-Admin Settings Endpoint

This module provides endpoints that can ONLY be accessed by the Owner-Admin.
These are system-critical settings that should not be accessible to regular admins.
"""

from flask import Blueprint, jsonify, request
from app.security.rbac import require_owner
from app.middleware.auth import token_required

# Create blueprint
owner_bp = Blueprint('owner', __name__, url_prefix='/api/v1/admin-panel/owner')


@owner_bp.route('/status', methods=['GET'])
@token_required
@require_owner()
def owner_status():
    """
    Get Owner-Admin status

    Only accessible by Owner-Admin.
    Returns information about the owner account and system.

    Returns:
        200: Owner status information
        403: Not owner-admin
    """
    from app.middleware.auth import get_current_user

    user = get_current_user()

    return jsonify({
        'success': True,
        'data': {
            'user_id': user.get('user_id'),
            'email': user.get('email'),
            'is_owner': True,
            'message': 'You are the Owner-Admin of this system'
        }
    }), 200


@owner_bp.route('/system-info', methods=['GET'])
@token_required
@require_owner()
def system_info():
    """
    Get system information

    Only accessible by Owner-Admin.
    Returns critical system information.

    Returns:
        200: System information
        403: Not owner-admin
    """
    import platform
    import psutil
    from datetime import datetime

    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return jsonify({
            'success': True,
            'data': {
                'system': {
                    'platform': platform.system(),
                    'platform_release': platform.release(),
                    'platform_version': platform.version(),
                    'architecture': platform.machine(),
                    'processor': platform.processor(),
                    'python_version': platform.python_version()
                },
                'resources': {
                    'cpu_percent': cpu_percent,
                    'memory_total': memory.total,
                    'memory_available': memory.available,
                    'memory_percent': memory.percent,
                    'disk_total': disk.total,
                    'disk_used': disk.used,
                    'disk_free': disk.free,
                    'disk_percent': disk.percent
                },
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SYSTEM_INFO_ERROR',
                'message': f'Could not retrieve system information: {str(e)}'
            }
        }), 500


@owner_bp.route('/settings', methods=['GET', 'PUT'])
@token_required
@require_owner()
def owner():
    """
    Get or update owner-specific settings

    Only accessible by Owner-Admin.

    GET: Returns current owner settings
    PUT: Updates owner settings

    Returns:
        200: Settings retrieved/updated
        403: Not owner-admin
    """
    if request.method == 'GET':
        # TODO: Retrieve owner settings from database
        return jsonify({
            'success': True,
            'data': {
                'message': 'Owner settings endpoint (GET)',
                'note': 'Implementation pending'
            }
        }), 200

    elif request.method == 'PUT':
        # TODO: Update owner settings
        return jsonify({
            'success': True,
            'data': {
                'message': 'Owner settings endpoint (PUT)',
                'note': 'Implementation pending'
            }
        }), 200


# Export blueprint
__all__ = ['owner_bp']
