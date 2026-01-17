"""Discussion Forums API"""

from flask import Blueprint, request, jsonify, g
from app.middleware.auth import token_required

forums_bp = Blueprint('forums', __name__, url_prefix='/community/forums')


@forums_bp.route('/api/community/forums', methods=['GET'])
@token_required
def get_forums():
    """Get all forums"""
    # TODO: Implement
    return jsonify({'success': True, 'forums': []}), 200
