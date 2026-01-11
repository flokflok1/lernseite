"""
Setup Wizard Security Middleware

Protects setup wizard endpoints after installation is complete.
Only allows read-only endpoints (/status, /verify) unless admin key is provided.
"""

import os
from functools import wraps
from flask import request, jsonify
from setup.install_check import InstallationChecker


# Setup Admin Key (set in .env for emergency access)
SETUP_ADMIN_KEY = os.getenv('SETUP_ADMIN_KEY', None)

# Read-only endpoints that are always allowed
READ_ONLY_ENDPOINTS = [
    '/setup/status',
    '/setup/verify',
    '/setup/verify/report'
]


def require_setup_access(f):
    """
    Decorator to protect setup wizard endpoints after installation.

    Rules:
    1. If system NOT installed → Allow all setup endpoints
    2. If system IS installed:
       - Read-only endpoints (/status, /verify) → Always allow
       - Write endpoints → Require SETUP_ADMIN_KEY header

    Usage:
        @setup_bp.route('/database', methods=['POST'])
        @require_setup_access
        def setup_database():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if system is installed
        is_installed = InstallationChecker.is_installed()

        # If NOT installed, allow everything
        if not is_installed:
            return f(*args, **kwargs)

        # System IS installed - check if endpoint is read-only
        if request.path in READ_ONLY_ENDPOINTS:
            return f(*args, **kwargs)

        # Write endpoint after installation - require admin key
        admin_key = request.headers.get('X-Setup-Admin-Key')

        if not SETUP_ADMIN_KEY:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SETUP_LOCKED',
                    'message': 'Setup wizard is locked after installation. '
                               'Set SETUP_ADMIN_KEY environment variable for emergency access.'
                }
            }), 403

        if admin_key != SETUP_ADMIN_KEY:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_ADMIN_KEY',
                    'message': 'Invalid setup admin key. Setup wizard is locked after installation.'
                }
            }), 403

        # Admin key valid - allow access
        return f(*args, **kwargs)

    return decorated_function


def setup_middleware_info():
    """
    Get info about setup security status

    Returns:
        dict: Security status information
    """
    is_installed = InstallationChecker.is_installed()
    has_admin_key = SETUP_ADMIN_KEY is not None

    return {
        'installed': is_installed,
        'setup_locked': is_installed,
        'admin_key_configured': has_admin_key,
        'read_only_endpoints': READ_ONLY_ENDPOINTS,
        'message': (
            'Setup wizard is open (system not installed)' if not is_installed
            else 'Setup wizard is locked (system installed). Only read-only endpoints available.'
        )
    }
