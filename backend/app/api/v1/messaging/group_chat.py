"""Group Chat API (Feature-Flagged)"""

from flask import Blueprint, request, jsonify, g
from app.api.middleware.auth import token_required
from app.core.feature_flags.flag_decorators import require_feature

group_chat_bp = Blueprint('group_chat', __name__, url_prefix='/messaging/groups')


@group_chat_bp.route('/api/messaging/group', methods=['POST'])
@token_required
@require_feature('group_chat')
def create_group():
    """Create group chat (Feature Flag: group_chat)"""
    data = request.get_json()
    # TODO: Create group
    return jsonify({'success': True, 'group_id': 'temp'}), 201
