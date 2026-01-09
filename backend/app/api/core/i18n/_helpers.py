"""
Shared helper functions for i18n API modules.
"""

import logging

logger = logging.getLogger(__name__)


def error_response(code: str, message: str, status: int = 400) -> tuple:
    """Create a standardized error response."""
    from flask import jsonify
    return jsonify({
        'success': False,
        'error': {'code': code, 'message': message}
    }), status


def success_response(data: dict = None, status: int = 200) -> tuple:
    """Create a standardized success response."""
    from flask import jsonify
    response = {'success': True}
    if data is not None:
        response['data'] = data
    return jsonify(response), status
