"""Study Groups API"""

from flask import Blueprint, request, jsonify, g
from app.middleware.auth import token_required

groups_bp = Blueprint('study_groups', __name__, url_prefix='/community/groups')


@groups_bp.route('/api/community/groups', methods=['GET'])
@token_required
def get_groups():
    """Get study groups"""
    # TODO: Implement
    return jsonify({'success': True, 'groups': []}), 200
