"""Direct Messages API (Feature-Flagged)"""

from flask import Blueprint, request, jsonify, g
from app.middleware.auth import token_required
from app.core.feature_flags.flag_decorators import require_feature

dm_bp = Blueprint('direct_messages', __name__, url_prefix='/messaging/dm')


@dm_bp.route('/api/messaging/dm', methods=['POST'])
@token_required
@require_feature('direct_messages')
def send_message():
    """Send direct message (Feature Flag: direct_messages)"""
    data = request.get_json()
    # TODO: Implement DM sending
    return jsonify({'success': True, 'message': 'DM sent'}), 201


@dm_bp.route('/api/messaging/dm/<recipient_id>', methods=['GET'])
@token_required
@require_feature('direct_messages')
def get_conversation(recipient_id):
    """Get conversation with user (Feature Flag: direct_messages)"""
    # TODO: Get messages
    return jsonify({'success': True, 'messages': []}), 200
