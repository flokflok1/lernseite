"""
NPC Tutor - System Feature

⚠️ STUB ONLY - TODO: Implementation
"""
from flask import Blueprint
from app.api.middleware.auth import token_required
from app.api.responses.responses import success_response

npc_tutor_bp = Blueprint('npc_tutor', __name__, url_prefix='/tutor/npc')

@npc_tutor_bp.route('/chat', methods=['POST'])
@token_required
def chat_with_tutor():
    return success_response(data={"status": "stub", "message": "NPC Tutor - Coming Soon"}, status_code=501)
